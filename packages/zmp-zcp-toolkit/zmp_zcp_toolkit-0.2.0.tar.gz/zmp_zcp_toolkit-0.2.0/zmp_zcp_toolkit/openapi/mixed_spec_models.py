from __future__ import annotations

from pathlib import Path
from typing import List, Union

from pydantic import BaseModel


class APISimpleSpec(BaseModel):
    path: str
    methods: List[str]


class APIConfig(BaseModel):
    file_path: Union[str, Path]
    apis: List[APISimpleSpec]


class BackendAPIConfig(BaseModel):
    backend: str
    config: APIConfig


class MixedAPISpecConfig(BaseModel):
    """
    MixedAPISpecConfig is a model that contains the configuration for the mixed backendAPI spec.

    ```json
    [
        {
            "backend": "zcp-alert-backend",
            "config": {
                "file_path": "openapi_spec/zcp_spec/alert_openapi_spec.json",
                "apis": [
                    {
                        "path":"/api/alert/v1/alerts",
                        "methods": ["get", "post"]
                    },
                    {
                        "path":"/api/alert/v1/alerts/webhook",
                        "methods": ["post", "get"]
                    },
                    {
                        "path":"/api/alert/v1/alert/priorities",
                        "methods": ["get"]
                    }
                ]
            }
        },
        {
            "backend": "example-backend",
            "config": {
                "file_path": "openapi_spec/zcp_spec/test_spec.json",
                "apis": [
                    {
                        "path":"/api/example/v1/test",
                        "methods": ["post"]
                    }
                ]
            }
        }
    ]
    ```
    """

    backends: List[BackendAPIConfig]
