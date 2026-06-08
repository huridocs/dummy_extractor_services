from pydantic import BaseModel

from data.UwaziCredentials import UwaziCredentials


class AIJobRequest(BaseModel):
    job_id: str | None = None
    message: str
    credentials: UwaziCredentials
