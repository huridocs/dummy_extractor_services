from queue_processor.QueueProcessor import QueueProcessor

from app import params_path

from data.MetadataExtractionTask import MetadataExtractionTask
from data.ResultsMessage import ResultsMessage


def process(message):
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

    return model_results_message.model_dump()

if __name__ == "__main__":
    queues_names = ["information_extraction", "development_information_extraction"]
    queue_processor = QueueProcessor("127.0.0.1", 6379, queues_names)
    queue_processor.start(process)
