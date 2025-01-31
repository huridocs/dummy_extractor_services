from pydantic import BaseModel

from data.ParagraphExtractorParams import ParagraphExtractorParams


class ParagraphExtractorTask(BaseModel):
    tenant: str
    task: str
    params: ParagraphExtractorParams