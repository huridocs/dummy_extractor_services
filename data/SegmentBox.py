from pydantic import BaseModel


class SegmentBox(BaseModel):
    left: float = 1
    top: float = 2
    width: float = 3
    height: float = 4
    page_number: int = 1
