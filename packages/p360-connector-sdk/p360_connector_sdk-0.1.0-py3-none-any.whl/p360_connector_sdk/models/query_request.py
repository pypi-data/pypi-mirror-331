from pydantic import BaseModel
from typing import Dict, Any, Optional


class QueryRequest(BaseModel):
    """
    Represents a request model for executing a query.

    Attributes:
        request_id (str): A unique identifier for the request.
        user (dict): A dictionary containing user details (e.g., user ID, role, security context etc..).
        metadata (dict): A dictionary containing any optional metadata required  to fulfil the request.
        curl (str): The cURL command representation of the external request (mutually exclusive with query_str).
        query_str (str): The actual query string to be executed (mutually exclusive with curl).
    """

    request_id: str
    user: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    curl: Optional[str] = None
    query_str: Optional[str] = None
