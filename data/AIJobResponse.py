from pydantic import BaseModel

from data.AIJobStatus import AIJobStatus


class AIJobResponse(BaseModel):
    job_id: str | None = None
    message: str
    status: AIJobStatus
