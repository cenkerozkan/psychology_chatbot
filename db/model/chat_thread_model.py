from pydantic import BaseModel

from .message_model import MessageModel

class ChatThreadModel(BaseModel):
    chat_name: str
    chat_id: str
    created_at: str
    updated_at: str
    history: list[MessageModel]