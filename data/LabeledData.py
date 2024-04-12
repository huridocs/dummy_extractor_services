from typing import List

from pydantic import BaseModel

from data.Option import Option
from data.SegmentBox import SegmentBox


class LabeledData(BaseModel):
    tenant: str = ""
    id: str = ""
    xml_file_name: str = ""
    entity_name: str = ""
    language_iso: str = ""
    label_text: str = ""
    values: list[Option] = list()
    source_text: str = ""
    page_width: float = 0
    page_height: float = 0
    xml_segments_boxes: list[SegmentBox] = list()
    label_segments_boxes: list[SegmentBox] = list()

    def correct_data_scale(self):
        self.label_segments_boxes = [x.correct_input_data_scale() for x in self.label_segments_boxes]
        return self
