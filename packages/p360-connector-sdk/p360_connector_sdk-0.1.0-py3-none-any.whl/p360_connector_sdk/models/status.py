from pydantic import BaseModel


class Status(BaseModel):
    """
    A model representing the status of a response or operation.

    Attributes:
        code (str): The status code representing the outcome.
        description (str): Brief description of the status.
    """

    code: str
    description: str
