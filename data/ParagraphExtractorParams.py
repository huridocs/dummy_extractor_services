from pydantic import BaseModel

from data.XML import XML


class ParagraphExtractorParams(BaseModel):
    extractor_id: str
    entity_id: str
    xmls: list[XML]
    metadata: dict[str, str] = dict()
