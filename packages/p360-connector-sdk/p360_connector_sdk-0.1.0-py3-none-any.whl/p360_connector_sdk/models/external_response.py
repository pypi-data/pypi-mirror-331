from pydantic import BaseModel
from typing import Dict, Any, Optional

from p360_connector_sdk.models.status import Status

class ExternalResponse(BaseModel):
    """
    A model representing an external API response.

    Attributes:
        status (Status): The status of the response, including code and description.
        headers (Dict[str, Any]): A dictionary containing response headers.
        payload (Any): The main content of the response, which can be of any type.
    """

    status: Status
    headers: Optional[Dict[str, Any]] = None
    payload: Optional[Any] = None
