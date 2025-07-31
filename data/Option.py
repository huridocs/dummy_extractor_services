from pydantic import BaseModel


class Option(BaseModel):
    id: str
    label: str
    segment_text: str = ""
