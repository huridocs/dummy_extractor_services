from typing import List

from pydantic import BaseModel

from data.Option import Option
from data.SegmentBox import SegmentBox


class Suggestion(BaseModel):
    tenant: str
    id: str
    xml_file_name: str
    text: str = ""
    values: List[Option] = list()
    segment_text: str
    page_number: int
    segments_boxes: List[SegmentBox]
