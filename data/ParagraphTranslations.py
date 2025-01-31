from pydantic import BaseModel

from data.ParagraphTranslation import ParagraphTranslation


class ParagraphTranslations(BaseModel):
    position: int
    translations: list[ParagraphTranslation]