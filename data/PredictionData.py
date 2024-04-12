from typing import List

from pydantic import BaseModel

from data.SegmentBox import SegmentBox


class PredictionData(BaseModel):
    tenant: str = ""
    id: str = ""
    entity_name: str = ""
    source_text: str = ""
    xml_file_name: str = ""
    page_width: float = 0
    page_height: float = 0
    xml_segments_boxes: list[SegmentBox] = list()
