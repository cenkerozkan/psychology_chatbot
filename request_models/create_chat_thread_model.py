from pydantic import BaseModel

class CreateChatThreadModel(BaseModel):
    user_uid: str
    chat_name: str