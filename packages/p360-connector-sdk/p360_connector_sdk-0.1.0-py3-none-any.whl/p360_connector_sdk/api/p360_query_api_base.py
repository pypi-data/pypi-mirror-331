from abc import ABC, abstractmethod

from p360_connector_sdk.models.query_request import QueryRequest
from p360_connector_sdk.models.query_response import QueryResponse


class P360QueryAPIBase(ABC):
    """
    An abstract base class that defines the interface for a P360 query API.

    This class enforces the implementation of query method that processes a query 
    request and returns a corresponding response.

    Methods:
        query(request: QueryRequest) -> QueryResponse:
            Abstract method to process a query request and return the response.
    """

    @abstractmethod
    def query(self, request: QueryRequest) -> QueryResponse:
        """
        Process the query and return the response.
        
        Args:
            request (QueryRequest): The query request payload.
        
        Returns:
            QueryResponse: The query response.
        """
