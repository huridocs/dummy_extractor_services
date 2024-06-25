from data.Translation import Translation
from data.TranslationTaskMessage import TranslationTaskMessage


class TranslationResponseMessage(TranslationTaskMessage):
    translations: list[Translation]


if __name__ == '__main__':
    t = TranslationTaskMessage(namespace="namespace", key="key", text="text", language_from="language_from", languages_to=["languages_to"])
    a = TranslationResponseMessage(**t.dict(), translations=[])
    print(a)