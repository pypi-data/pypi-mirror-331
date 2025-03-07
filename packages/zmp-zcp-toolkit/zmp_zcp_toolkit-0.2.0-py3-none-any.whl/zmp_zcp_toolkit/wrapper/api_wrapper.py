import logging
from typing import Any, List

from zmp_zcp_toolkit.openapi.mixed_spec_models import MixedAPISpecConfig, Operation
from zmp_zcp_toolkit.openapi.openapi_utils import OpenAPIHelper
from zmp_zcp_toolkit.wrapper.base import BaseAPIWrapper

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ZmpAPIWrapper(BaseAPIWrapper):
    """Wrapper for ZMP API."""

    def __init__(self, mixed_api_spec_config: MixedAPISpecConfig):
        self.open_api_helper = OpenAPIHelper(
            mixed_api_spec_config=mixed_api_spec_config
        )

    def get_operations(self) -> List[Operation]:
        return self.open_api_helper.generate_operations()

    def run(
        self,
        method: str,
        path: str,
        /,
        *,
        path_params: Any = None,
        query_params: Any = None,
        request_body: Any = None,
    ) -> str:
        """Run the API request.

        Args:
            method (str): The HTTP method to use
            path (str): The path to the resource
            path_params (Any, optional): Path parameters for the tool. Defaults to None.
            query_params (Any, optional): Query parameters for the tool. Defaults to None.
            request_body (Any, optional): Request body for the tool. Defaults to None.

        Returns:
            str: Response from the API
        """
        logger.debug(f"Method: {method}, Path: {path}")
        logger.debug("-" * 100)
        logger.debug(f"Path params: {path_params}")
        logger.debug(f"Query params: {query_params}")
        logger.debug(f"Request body: {request_body}")

        if path_params is not None:
            path = path.format(**path_params)  # for path parameters
            logger.debug(f"Formatted path: {path}")

        response = self.client.request(
            method, path, params=query_params, json=request_body
        )

        return self.get_response(response)
