import json
import os
import random
import sys
from os.path import exists
from pathlib import Path
from time import sleep

from fastapi import FastAPI, UploadFile, File, Form
from queue_processor.QueueProcessor import QueueProcessor
from starlette.responses import PlainTextResponse

from data.ExtractionData import ExtractionData
from data.LabeledData import LabeledData
from data.Options import Options
from data.ParagraphExtractionData import ParagraphExtractionData
from data.ParagraphExtractionResultsMessage import ParagraphExtractionResultsMessage
from data.ParagraphTranslation import ParagraphTranslation
from data.ParagraphTranslations import ParagraphTranslations
from data.ParagraphsTranslations import ParagraphsTranslations
from data.PredictionData import PredictionData
from data.SegmentBox import SegmentBox
from data.Suggestion import Suggestion
from data.XML import XML

app = FastAPI()

data_path = Path("data.json")
params_path = Path("params.json")
options_path = Path("options.json")


@app.get("/info")
async def info():
    return sys.version


@app.post("/async_extraction/{tenant}")
async def async_extraction(tenant, file: UploadFile = File(...)):
    return "task registered"


@app.post("/set_paragraphs")
async def set_paragraphs(extraction_data: ExtractionData):
    return "paragraphs saved"


@app.get("/get_paragraphs/{tenant}/{pdf_file_name}")
async def get_paragraphs(tenant: str, pdf_file_name: str):
    print("get_paragraphs", tenant, pdf_file_name)
    extraction_data = ExtractionData(
        tenant=tenant, file_name=pdf_file_name, paragraphs=[SegmentBox()], page_height=0, page_width=0
    )
    return extraction_data.model_dump_json()


@app.get("/get_xml/{tenant}/{pdf_file_name}", response_class=PlainTextResponse)
async def get_xml():
    with open(f"test.xml", mode="r") as file:
        content = file.read()
        return content


@app.post("/xml_to_train/{tenant}/{extractor_id}")
async def to_train_xml_file(tenant, extractor_id, file: UploadFile = File(...)):
    return "xml_to_train saved"


@app.post("/xml_to_predict/{tenant}/{extractor_id}")
async def to_predict_xml_file(tenant, extractor_id, file: UploadFile = File(...)):
    return "xml_to_train saved"


@app.post("/labeled_data")
async def labeled_data_post(labeled_data: LabeledData):
    return "labeled data saved"


@app.post("/prediction_data")
async def prediction_data_post(prediction_data: PredictionData):
    predictions_data = json.loads(data_path.read_text()) if exists(data_path) else list()
    predictions_data.append(prediction_data.model_dump())
    data_path.write_text(json.dumps(predictions_data))
    return "prediction data saved"


@app.get("/get_suggestions/{tenant}/{extractor_id}")
async def get_suggestions(tenant: str, extractor_id: str):
    predictions_data = json.loads(data_path.read_text()) if exists(data_path) else list()

    suggestions_list = list()
    params = json.loads(params_path.read_text()) if exists(params_path) else dict()
    params["options"] = params["options"] if params and "options" in params else list()
    if options_path.exists() and not params["options"]:
        params["options"] = json.loads(options_path.read_text())

    all_values = params["options"] if params and "options" in params else list()
    multi_value = params["multi_value"] if params and "multi_value" in params else False

    for prediction_data in predictions_data:
        values_count = random.randint(1, len(all_values)) if multi_value else 1
        values = random.sample(all_values, k=values_count) if all_values else list()
        suggestions_list.append(
            Suggestion(
                tenant=tenant,
                id=extractor_id,
                xml_file_name=prediction_data["xml_file_name"],
                entity_name=prediction_data["entity_name"],
                text="2023" if not values else " ".join([option["label"] for option in values]),
                values=values,
                segment_text="2023" if not values else " ".join([option["label"] for option in values]),
                page_number=1,
                segments_boxes=[SegmentBox(left=0, top=0, width=250, height=250, page_number=1)],
            ).model_dump()
        )

    if exists(data_path):
        os.remove(data_path)

    if exists(params_path):
        os.remove(params_path)

    sleep(5)
    return json.dumps(suggestions_list)


@app.post("/extract_paragraphs")
async def extract_paragraphs(json_data: str = Form(...), xml_files: list[UploadFile] = File(...)):
    paragraph_extraction_data = ParagraphExtractionData(**json.loads(json_data))
    params_path.write_text(paragraph_extraction_data.model_dump_json())
    for xml_file in xml_files:
        print(f"Processing XML file: {xml_file.filename}")

    print(f"Extracting paragraphs for {paragraph_extraction_data.model_dump_json()}")
    queue_name = "development_extract_paragraphs_results"
    result = ParagraphExtractionResultsMessage(
        key=paragraph_extraction_data.key,
        xmls=[
            XML(xml_file_name=x.xml_file_name, language=x.language, is_main_xml=x.is_main_language)
            for x in paragraph_extraction_data.xmls
        ],
        success=True,
        error_message="",
        data_url=f"http://127.0.0.1:5056/get_paragraphs_translations/{paragraph_extraction_data.key}",
    )
    queue = QueueProcessor("127.0.0.1", 6379, []).get_queue(queue_name)
    queue.sendMessage().message(result.model_dump()).execute()
    return "ok"


@app.get("/get_paragraphs_translations/{key}")
async def get_paragraphs_translations(key: str):
    paragraph_extraction_data = ParagraphExtractionData(**json.loads(params_path.read_text()))

    main_language = [x.language for x in paragraph_extraction_data.xmls if x.is_main_language][0]
    languages = [x.language for x in paragraph_extraction_data.xmls]

    paragraphs: list[ParagraphTranslations] = list()
    for i in range(2):
        translations = list()
        for language in languages:
            translation = ParagraphTranslation(
                language=language, text=f"paragraph {i} in {language}", needs_user_review=False
            )
            translations.append(translation)

        paragraph = ParagraphTranslations(position=i + 1, translations=translations)
        paragraphs.append(paragraph)

    paragraphs_translations = ParagraphsTranslations(
        key=key, main_language=main_language, available_languages=languages, paragraphs=paragraphs
    )

    sleep(5)
    return paragraphs_translations


@app.post("/options")
def save_options(options: Options):
    options_list = [option.model_dump() for option in options.options]
    options_path.write_text(json.dumps(options_list))
    return True
