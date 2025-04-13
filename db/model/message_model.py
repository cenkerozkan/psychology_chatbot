from pydantic import BaseModel

class MessageModel(BaseModel):
    created_at: str
    role: str
    content: str