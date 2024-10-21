from typing import List

from pydantic import BaseModel

from data.Option import Option
from data.SegmentBox import SegmentBox


class Suggestion(BaseModel):
    tenant: str
    id: str
    xml_file_name: str = ""
    entity_name: str = ""
    text: str = ""
    values: List[Option] = list()
    # empty_suggestion: bool = False
    segment_text: str = ""
    page_number: int = 1
    segments_boxes: List[SegmentBox] = list()
