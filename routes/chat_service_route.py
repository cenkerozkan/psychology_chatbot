from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from service.chat_service import chat_service
from repository.context_repository import context_repository

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    chat_name: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    chat_id: str


class ChatThreadResponse(BaseModel):
    chat_id: str
    chat_name: str
    created_at: str
    updated_at: str


@router.post("/send", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest):
    """
    Send a message to the chatbot and get a response.
    If chat_id is provided, it will use an existing chat thread.
    If not, it will create a new one with the provided chat_name or a default name.
    """
    chat_thread = None

    # Use existing chat if chat_id is provided
    if chat_request.chat_id:
        chat_thread = await context_repository.get_one_by_id(chat_request.chat_id)
        if not chat_thread:
            raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_request.chat_id} not found")

    # Create new chat if no chat_id or chat not found
    if not chat_thread:
        chat_name = chat_request.chat_name or f"Chat {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        chat_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()

        chat_thread = ChatThreadModel(
            chat_id=chat_id,
            chat_name=chat_name,
            created_at=now,
            updated_at=now,
            history=[]
        )

        # Save the new chat thread
        await context_repository.insert_one(chat_thread)

    # Send message and get response
    response = await chat_service.send_message(chat_request.message, chat_thread)

    return ChatResponse(
        message=response,
        chat_id=chat_thread.chat_id
    )


@router.get("/threads", response_model=List[ChatThreadResponse])
async def get_all_chats():
    """
    Get all available chat threads.
    """
    threads = await context_repository.get_all()
    return [
        ChatThreadResponse(
            chat_id=thread.chat_id,
            chat_name=thread.chat_name,
            created_at=thread.created_at,
            updated_at=thread.updated_at
        ) for thread in threads
    ]


@router.get("/threads/{chat_id}/messages")
async def get_chat_history(chat_id: str):
    """
    Get the message history for a specific chat thread.
    """
    chat_thread = await context_repository.get_one_by_id(chat_id)
    if not chat_thread:
        raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_id} not found")

    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at
        } for msg in chat_thread.history
    ]


@router.delete("/threads/{chat_id}")
async def delete_chat(chat_id: str):
    """
    Delete a chat thread.
    """
    chat_thread = await context_repository.get_one_by_id(chat_id)
    if not chat_thread:
        raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_id} not found")

    result = await context_repository.delete_one(chat_id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to delete chat thread")

    return {"message": f"Chat thread {chat_id} deleted successfully"}


@router.post("/threads", response_model=ChatThreadResponse)
async def create_chat_thread(chat_name: str = None):
    """
    Create a new empty chat thread.
    """
    # Generate default name if none provided
    if not chat_name:
        chat_name = f"Chat {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    chat_id = str(uuid.uuid4())
    now = datetime.datetime.now().isoformat()

    chat_thread = ChatThreadModel(
        chat_id=chat_id,
        chat_name=chat_name,
        created_at=now,
        updated_at=now,
        history=[]
    )

    # Save the new chat thread
    await context_repository.insert_one(chat_thread)

    return ChatThreadResponse(
        chat_id=chat_thread.chat_id,
        chat_name=chat_thread.chat_name,
        created_at=chat_thread.created_at,
        updated_at=chat_thread.updated_at
    )