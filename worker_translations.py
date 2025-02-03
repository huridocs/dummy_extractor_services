from queue_processor.QueueProcessor import QueueProcessor

from data.Translation import Translation
from data.TranslationResponseMessage import TranslationResponseMessage
from data.TranslationTaskMessage import TranslationTaskMessage


def process(message):
    task = TranslationTaskMessage(**message)
    print(task.model_dump())

    translations: list[Translation] = [get_translation(task, language) for language in task.languages_to]
    response = TranslationResponseMessage(
        **task.model_dump(),
        translations=translations,
    )

    return response.model_dump()


def get_translation(translation_task_message: TranslationTaskMessage, language: str) -> Translation:
    if language == "error":
        return Translation(text="", language=language, success=False, error_message="service error")

    text = f"[translation for {language}] {translation_task_message.text}"
    return Translation(text=text, language=language, success=True, error_message="")


if __name__ == "__main__":
    queues_names = ["translations", "development_translations"]
    queue_processor = QueueProcessor("127.0.0.1", 6379, queues_names)
    queue_processor.start(process)
