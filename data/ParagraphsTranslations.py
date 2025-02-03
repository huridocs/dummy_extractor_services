from pydantic import BaseModel

from data.ParagraphTranslations import ParagraphTranslations


class ParagraphsTranslations(BaseModel):
    key: str
    main_language: str
    available_languages: list[str]
    paragraphs: list[ParagraphTranslations]
