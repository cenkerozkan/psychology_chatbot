from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncIterator
import uuid
import datetime
import os
import json
import asyncio

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from service.chat_service import chat_service
from repository.context_repository import context_repository

router = APIRouter(prefix="/api/chat", tags=["chat"])

# API Key security
API_KEY = os.getenv("API_KEY", "default-dev-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key"""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    chat_id: str

class ChatThreadResponse(BaseModel):
    chat_id: str
    chat_name: str
    created_at: str
    updated_at: str

import json

async def event_generator(chat_request: ChatRequest, chat_thread: ChatThreadModel) -> AsyncIterator[str]:
    """Generate SSE events for streaming response"""
    # First yield the chat_id so the client knows which chat this belongs to
    yield f"data: {json.dumps({'chat_id': chat_thread.chat_id}, ensure_ascii=False)}\n\n"

    # Send message to get response
    full_response = await chat_service.send_message(chat_request.message, chat_thread)

    # Split the response into words and yield them as SSE events
    words = full_response.split()
    for i in range(0, len(words), 3):  # Send 3 words at a time
        chunk = " ".join(words[i:i+3])
        yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.1)

    # Send a completion event
    yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

@router.post("/send/stream")
async def send_message_stream(chat_request: ChatRequest, api_key: APIKey = Depends(get_api_key)):
    """
    Send a message to the chatbot and get a streaming response using SSE.
    """
    chat_thread = None

    # Use existing chat if chat_id is provided
    if chat_request.chat_id:
        chat_thread = await context_repository.get_one_by_id(chat_request.chat_id)
        if not chat_thread:
            raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_request.chat_id} not found")

    # Create new chat if no chat_id or chat not found
    if not chat_thread:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        chat_name = f"Chat_{today}"
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

    return StreamingResponse(
        event_generator(chat_request, chat_thread),
        media_type="text/event-stream"
    )

@router.post("/send", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest, api_key: APIKey = Depends(get_api_key)):
    """
    Send a message to the chatbot and get a response.
    If chat_id is provided, it will use an existing chat thread.
    If not, it will create a new one with today's date.
    """
    chat_thread = None

    # Use existing chat if chat_id is provided
    if chat_request.chat_id:
        chat_thread = await context_repository.get_one_by_id(chat_request.chat_id)
        if not chat_thread:
            raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_request.chat_id} not found")

    # Create new chat if no chat_id or chat not found
    if not chat_thread:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        chat_name = f"Chat_{today}"
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

@router.post("/create-daily", response_model=ChatThreadResponse)
async def create_daily_chat(api_key: APIKey = Depends(get_api_key)):
    """
    Create a new daily chat thread.
    Mobile clients should call this at the start of a new day.
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    chat_name = f"Chat_{today}"
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

@router.get("/threads", response_model=List[ChatThreadResponse])
async def get_all_chats(api_key: APIKey = Depends(get_api_key)):
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
async def get_chat_history(chat_id: str, api_key: APIKey = Depends(get_api_key)):
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
async def delete_chat(chat_id: str, api_key: APIKey = Depends(get_api_key)):
    """
    Delete a chat thread.
    """
    chat_thread = await context_repository.get_one_by_id(chat_id)
    if not chat_thread:
        raise HTTPException(status_code=404, detail=f"Chat thread with ID {chat_id} not found")

    result = await context_repository.delete_one_by_id(chat_id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to delete chat thread")

    return {"message": f"Chat thread {chat_id} deleted successfully"}