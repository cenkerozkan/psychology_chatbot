from pydantic import BaseModel

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: dict