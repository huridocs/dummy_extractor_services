from pydantic import BaseModel

from data.AIJobStatus import AIJobStatus


class AIJobStatusResponse(BaseModel):
    job_id: str
    result: str | None = None
    status: AIJobStatus
