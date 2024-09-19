from queue_processor.QueueProcessor import QueueProcessor

from data.ExtractionMessage import ExtractionMessage
from data.Task import Task

def process(message):
    task = Task(**message)
    print(task.model_dump())
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

    return extraction_message.model_dump()


if __name__ == "__main__":
    queues_names = ["segmentation", "development_segmentation"]
    queue_processor = QueueProcessor("127.0.0.1", 6379, queues_names)
    queue_processor.start(process)
