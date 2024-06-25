from pydantic import BaseModel


class TranslationTaskMessage(BaseModel):
    namespace: str
    key: str | list[str]
    text: str
    language_from: str
    languages_to: list[str]

