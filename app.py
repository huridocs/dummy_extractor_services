import json
import os
import sys
from os.path import exists
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from starlette.responses import PlainTextResponse

from data.ExtractionData import ExtractionData
from data.LabeledData import LabeledData
from data.PredictionData import PredictionData
from data.SegmentBox import SegmentBox
from data.Suggestion import Suggestion

app = FastAPI()

data_path = Path("data.json")
options_path = Path("options.json")


@app.get("/info")
async def info():
    return sys.version


@app.post("/async_extraction/{tenant}")
async def async_extraction(tenant, file: UploadFile = File(...)):
    return "task registered"


@app.get("/get_paragraphs/{tenant}/{pdf_file_name}")
async def get_paragraphs(tenant: str, pdf_file_name: str):
    print("get_paragraphs", tenant, pdf_file_name)
    extraction_data = ExtractionData(tenant=tenant, file_name=pdf_file_name, paragraphs=[], page_height=0, page_width=0)
    return extraction_data.json()


@app.get("/get_xml/{tenant}/{pdf_file_name}", response_class=PlainTextResponse)
async def get_xml():
    with open(f"test.xml", mode="r") as file:
        content = file.read()
        return content


@app.post("/xml_to_train/{tenant}/{extractor_id}")
async def to_train_xml_file(tenant, extractor_id, file: UploadFile = File(...)):
    print(to_train_xml_file, tenant, extractor_id)
    return "xml_to_train saved"


@app.post("/xml_to_predict/{tenant}/{extractor_id}")
async def to_predict_xml_file(tenant, extractor_id, file: UploadFile = File(...)):
    print(to_predict_xml_file, tenant, extractor_id)
    return "xml_to_train saved"


@app.post("/labeled_data")
async def labeled_data_post(labeled_data: LabeledData):
    return "labeled data saved"


@app.post("/prediction_data")
async def prediction_data_post(prediction_data: PredictionData):
    predictions_data = json.loads(data_path.read_text()) if exists(data_path) else list()
    predictions_data.append(prediction_data.dict())
    data_path.write_text(json.dumps(predictions_data))
    return "prediction data saved"


@app.get("/get_suggestions/{tenant}/{extractor_id}")
async def get_suggestions(tenant: str, extractor_id: str):
    predictions_data = json.loads(data_path.read_text()) if exists(data_path) else list()

    suggestions_list: list[dict[str, str]] = list()
    options = json.loads(options_path.read_text()) if exists(options_path) else list()
    for prediction_data in predictions_data:
        suggestions_list.append(
            Suggestion(
                tenant=tenant,
                id=extractor_id,
                xml_file_name=prediction_data["xml_file_name"],
                text="2023" if not options else ' '.join([option.label for option in options]),
                options=options,
                segment_text="2023" if not options else ' '.join([option.label for option in options]),
                page_number=1,
                segments_boxes=[SegmentBox(left=0, top=0, width=250, height=250, page_number=1)],
            ).dict()
        )

    if exists(data_path):
        os.remove(data_path)

    if exists(options_path):
        os.remove(options_path)

    return json.dumps(suggestions_list)
