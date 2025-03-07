from __future__ import annotations

from typing import Optional, Type

from pydantic import BaseModel


class ZmpAPIOperation(BaseModel):
    mode: str
    name: str
    description: str
    path: str
    method: str
    path_params: Optional[Type[BaseModel]]
    query_params: Optional[Type[BaseModel]]
    request_body: Optional[Type[BaseModel]]
