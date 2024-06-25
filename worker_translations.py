from time import sleep

import redis
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ, cmd

from data.Translation import Translation
from data.TranslationResponseMessage import TranslationResponseMessage
from data.TranslationTaskMessage import TranslationTaskMessage


class QueueProcessor:
    def __init__(self):
        self.task_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="translations_tasks",
        )

        self.results_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="translations_results",
        )

    def process(self, id, message, rc, ts):
        task = TranslationTaskMessage(**message)
        print(task.dict())

        translations: list[Translation] = [self.get_translation(task, language) for language in task.languages_to]
        response = TranslationResponseMessage(
            **task.dict(),
            translations=translations,
        )

        self.results_queue.sendMessage(delay=5).message(response.dict()).execute()
        return True

    def subscribe_to_tasks_queue(self):
        print("Translation queue processor started")
        while True:
            try:
                self.task_queue.getQueueAttributes().exec_command()
                self.results_queue.getQueueAttributes().exec_command()

                redis_smq_consumer = RedisSMQConsumer(
                    qname="translations_tasks",
                    processor=self.process,
                    host="127.0.0.1",
                    port=6379,
                )
                redis_smq_consumer.run()
            except redis.exceptions.ConnectionError:
                sleep(20)
            except cmd.exceptions.QueueDoesNotExist:
                self.task_queue.createQueue().exceptions(False).execute()
                self.results_queue.createQueue().exceptions(False).execute()

    @staticmethod
    def get_translation(translation_task_message: TranslationTaskMessage, language: str) -> Translation:
        if language == "error":
            return Translation(text="", language=language, success=False, error_message="service error")

        text = f"[translation for {language}] {translation_task_message.text}"
        return Translation(text=text, language=language, success=False, error_message="")


if __name__ == "__main__":
    queue_processor = QueueProcessor()
    queue_processor.subscribe_to_tasks_queue()
