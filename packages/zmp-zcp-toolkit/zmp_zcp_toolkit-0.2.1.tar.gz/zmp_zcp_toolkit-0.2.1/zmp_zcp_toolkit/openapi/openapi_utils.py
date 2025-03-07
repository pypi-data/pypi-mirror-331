from __future__ import annotations

import logging
import re
from typing import List

from zmp_zcp_toolkit.models.base import ZmpAPIOperation
from zmp_zcp_toolkit.openapi.fastapi_models import Operation
from zmp_zcp_toolkit.openapi.mixed_spec_models import MixedAPISpecConfig
from zmp_zcp_toolkit.openapi.zmpapi_models import ZmpOpenAPI

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class OpenAPIHelper:
    """OpenAPIHelper for ZMP ApiWrapper"""

    def __init__(self, mixed_api_spec_config: MixedAPISpecConfig):
        self.mixed_api_spec_config = mixed_api_spec_config

    def generate_operations(self) -> List[ZmpAPIOperation]:
        operations = []

        for backend in self.mixed_api_spec_config.backends:
            zmp_openapi = ZmpOpenAPI.from_spec_file(backend.config.file_path)

            for api in backend.config.apis:
                for method in api.methods:
                    operation: Operation = zmp_openapi.get_operation_by_path_method(
                        path=api.path,
                        method=method,
                    )
                    query_params, path_params, request_body = (
                        zmp_openapi.generate_models_by_path_and_method(
                            path=api.path,
                            method=method,
                        )
                    )

                    replaced_path = re.sub(
                        r"[/{}_]", "-", api.path
                    )  # remove path params brackets

                    name = "".join(
                        word.capitalize() for word in replaced_path.split("-")
                    )

                    logger.debug(f"name: {name}")

                    operations.append(
                        ZmpAPIOperation(
                            mode=name,
                            name=name,
                            description=operation.description
                            if operation.description
                            else "",  # Oops, description is mandatory for LLM
                            path=api.path,
                            method=method,
                            query_params=query_params,
                            path_params=path_params,
                            request_body=request_body,
                        )
                    )

        return operations
