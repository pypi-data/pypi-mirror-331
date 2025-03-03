from pydantic import BaseModel

from p360_connector_sdk.models.external_response import ExternalResponse


# from p360_connector_sdk.models import ExternalResponse


class QueryResponse(BaseModel):
    """
    A model representing the response to a query request.

    Attributes:
        request_id (str): A unique identifier for the query request.
        response (ExternalResponse): The external response containing status, headers, and payload.
    """

    request_id: str                                 
    response: ExternalResponse
