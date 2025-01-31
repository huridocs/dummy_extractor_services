from pydantic import BaseModel

from data.ParagraphTranslations import ParagraphTranslations


class ParagraphsTranslations(BaseModel):
    tenant: str
    extraction_id: str
    entity_id: str
    main_language: str
    available_languages: list[str]
    paragraphs: list[ParagraphTranslations]