from pydantic import BaseModel

from data.TokenType import TokenType


class SegmentBox(BaseModel):
    left: float = 1
    top: float = 2
    width: float = 3
    height: float = 4
    page_number: int = 1
    # page_width: int = 600
    # page_height: int = 800
    # text: str = ""
    segment_type: TokenType = TokenType.TEXT
