from time import sleep

import redis
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ, cmd

from data.ExtractionMessage import ExtractionMessage
from data.Task import Task


class QueueProcessor:
    def __init__(self):
        self.task_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="segmentation_tasks",
        )

        self.results_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="segmentation_results",
        )

    def process(self, id, message, rc, ts):
        task = Task(**message)
        print(task.dict())
        service_url = f"http://127.0.0.1:5051"
        results_url = f"{service_url}/get_paragraphs/{task.tenant}/{task.params.filename}"
        file_results_url = f"{service_url}/get_xml/{task.tenant}/{task.params.filename}"
        extraction_message = ExtractionMessage(
            tenant=task.tenant,
            task=task.task,
            params=task.params,
            success=True,
            data_url=results_url,
            file_url=file_results_url,
        )

        self.results_queue.sendMessage(delay=5).message(extraction_message.dict()).execute()
        return True

    def subscribe_to_tasks_queue(self):
        while True:
            try:
                self.task_queue.getQueueAttributes().exec_command()
                self.results_queue.getQueueAttributes().exec_command()

                redis_smq_consumer = RedisSMQConsumer(
                    qname="segmentation_tasks",
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


if __name__ == "__main__":
    queue_processor = QueueProcessor()
    queue_processor.subscribe_to_tasks_queue()
