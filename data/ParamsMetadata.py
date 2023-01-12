from typing import Optional, List

from pydantic import BaseModel

from data.Option import Option


class ParamsMetadata(BaseModel):
    property_name: str
    options: Optional[List[Option]] = None
    multi_value: bool = False
