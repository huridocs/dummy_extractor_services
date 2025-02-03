from pydantic import BaseModel


class XmlSegmentBox(BaseModel):
    left: float
    top: float
    width: float
    height: float
    page_number: int


class XmlData(BaseModel):
    xml_file_name: str
    language: str
    main_language: bool
    page_width: float
    page_height: float
    xml_segments_boxes: list[XmlSegmentBox]


class ParagraphExtractionData(BaseModel):
    key: str
    xmls: list[XmlData]
