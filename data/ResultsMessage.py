from pydantic import BaseModel

from data.ParamsMetadata import ParamsMetadata


class ResultsMessage(BaseModel):
    tenant: str
    task: str
    params: ParamsMetadata
    success: bool
    error_message: str
    data_url: str = None
