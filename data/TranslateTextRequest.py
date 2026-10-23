from pydantic import BaseModel


class TranslateTextRequest(BaseModel):
    text: str
    language_from: str
    language_to: str
