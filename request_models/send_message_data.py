from pydantic import BaseModel

class SendMessageData(BaseModel):
    chat_id: str
    message: str