from time import sleep

import redis
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ, cmd

from data.MetadataExtractionTask import MetadataExtractionTask
from data.ResultsMessage import ResultsMessage


class QueueProcessor:
    def __init__(self):
        self.task_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="information_extraction_tasks",
        )

        self.results_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="information_extraction_results",
        )

    def process(self, id, message, rc, ts):
        task = MetadataExtractionTask(**message)

        data_url = f"http://localhost:5052/get_suggestions/{task.tenant}/{task.params.property_name}"

        model_results_message = ResultsMessage(
            tenant=task.tenant,
            task=task.task,
            params=task.params,
            success=True,
            error_message="",
            data_url=data_url,
        )

        self.results_queue.sendMessage().message(model_results_message.dict()).execute()
        return True

    def subscribe_to_tasks_queue(self):
        while True:
            try:
                self.task_queue.getQueueAttributes().exec_command()
                self.results_queue.getQueueAttributes().exec_command()

                redis_smq_consumer = RedisSMQConsumer(
                    qname="information_extraction_tasks",
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
