from data.Translation import Translation
from data.TranslationTaskMessage import TranslationTaskMessage


class TranslationResponseMessage(TranslationTaskMessage):
    translations: list[Translation]


if __name__ == "__main__":
    t = TranslationTaskMessage(key=["key"], text="text", language_from="language_from", languages_to=["languages_to"])
    a = TranslationResponseMessage(**t.model_dump(), translations=[])
    print(a)
