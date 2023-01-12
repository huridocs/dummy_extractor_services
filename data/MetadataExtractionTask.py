from pydantic import BaseModel

from data.ParamsMetadata import ParamsMetadata


class MetadataExtractionTask(BaseModel):
    tenant: str
    task: str
    params: ParamsMetadata
