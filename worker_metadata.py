from time import sleep, time

import redis
from rsmq.consumer import RedisSMQConsumer
from rsmq import RedisSMQ, cmd

from app import params_path
from data.LogsMessage import LogsMessage, Severity
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

        self.logs_queue = RedisSMQ(
            host="127.0.0.1",
            port=6379,
            qname="information_extraction_logs",
        )

    def process(self, id, message, rc, ts):
        task = MetadataExtractionTask(**message)

        if task.params.options:
            params_path.write_text(task.params.model_dump_json())

        data_url = f"http://127.0.0.1:5056/get_suggestions/{task.tenant}/{task.params.id}"

        model_results_message = ResultsMessage(
            tenant=task.tenant,
            task=task.task,
            params=task.params,
            success=True,
            error_message="",
            data_url=data_url,
        )

        self.send_logs(task)
        self.results_queue.sendMessage().message(model_results_message.dict()).execute()
        return True

    def delete_old_messages(self):
        message = self.logs_queue.receiveMessage().exceptions(False).execute()

        while message and message["ts"] < time() - 2 * 60 * 60 * 24:
            self.logs_queue.deleteMessage(id=message["id"]).execute()
            message = self.logs_queue.receiveMessage().exceptions(False).execute()

    def send_logs(self, task):
        self.delete_old_messages()

        log_message = LogsMessage(
            tenant=task.tenant,
            extraction_name=task.params.id,
            severity=Severity.error,
            message="Error log example from dummy services",
        )

        self.logs_queue.sendMessage().message(log_message.dump()).execute()

        log_message = LogsMessage(
            tenant=task.tenant,
            extraction_name=task.params.id,
            severity=Severity.info,
            message="Information log example from dummy services",
        )

        self.logs_queue.sendMessage().message(log_message.dump()).execute()

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
