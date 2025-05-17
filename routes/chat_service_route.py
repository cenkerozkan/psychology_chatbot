from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse
import os
import asyncio

from starlette.responses import JSONResponse

from db.model.chat_thread_model import ChatThreadModel
from util.logger import get_logger
from request_models.create_chat_thread_model import CreateChatThreadModel
from request_models.send_message_data import SendMessageData
from response_models.response_model import ResponseModel
from service.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["Khatwa Chat Service"])
logger = get_logger(__name__)

# API Key security
API_KEY = os.getenv("API_KEY", "default-dev-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key: str = Security(api_key_header)) -> bool:
    if api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {api_key[:5]}...")
        return False
    return True

@router.post("/create_chat_thread")
async def create_chat_thread(
        request_data: CreateChatThreadModel,
        api_key: str = Depends(get_api_key)
) -> JSONResponse:
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid API key", "data": {}})
    create_thread: dict = await chat_service.create_chat_thread(**request_data.model_dump())
    return JSONResponse(
        status_code=create_thread.get("code"),
        content=ResponseModel(
            success=create_thread.get("success"),
            message=create_thread.get("message"),
            data=create_thread.get("data"),
        ).model_dump())

@router.get("/get_all_chats/{user_uid}")
async def get_all_chats(
        user_uid: str,
        api_key: str = Depends(get_api_key)
) -> JSONResponse:
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid API key", "data": {}})
    get_chats: dict = await chat_service.get_all_chats(user_uid)
    return JSONResponse(
        status_code=get_chats.get("code"),
        content=ResponseModel(
            success=get_chats.get("success"),
            message=get_chats.get("message"),
            data=get_chats.get("data"),
        ).model_dump())

@router.get("/get_chat_history/{chat_id}")
async def get_chat_history(
        chat_id: str,
        api_key: str = Depends(get_api_key)
) -> JSONResponse:
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid API key", "data": {}})
    chat_history: dict = await chat_service.get_chat_history(chat_id)
    return JSONResponse(
        status_code=chat_history.get("code"),
        content=ResponseModel(
            success=chat_history.get("success"),
            message=chat_history.get("message"),
            data=chat_history.get("data"),
        ).model_dump())

@router.delete("delete_chat_thread/{chat_id}")
async def delete_chat_thread(
        chat_id: str,
        api_key: str = Depends(get_api_key)
) -> JSONResponse:
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid API key", "data": {}})
    delete_thread: dict = await chat_service.delete_chat_thread(chat_id)
    return JSONResponse(
        status_code=delete_thread.get("code"),
        content=ResponseModel(
            success=delete_thread.get("success"),
            message=delete_thread.get("message"),
            data=delete_thread.get("data"),
        ).model_dump()
)

@router.patch("/update_chat_name/{chat_id}/{new_chat_name}")
async def update_chat_name(
        chat_id: str,
        new_chat_name: str,
        api_key: str = Depends(get_api_key)
) -> JSONResponse:
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid API key", "data": {}})
    update_thread: dict = await chat_service.update_chat_name(chat_id, new_chat_name)
    return JSONResponse(
        status_code=update_thread.get("code"),
        content=ResponseModel(
            success=update_thread.get("success"),
            message=update_thread.get("message"),
            data=update_thread.get("data"),
        ).model_dump()
)


@router.post("/send_message")
async def send_message(
        message_data: SendMessageData,
        api_key: str = Depends(get_api_key)
):
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={
                "success": False, "message": "Invalid API key", "data": {}})

    chat_thread: dict = await chat_service.get_one_chat(message_data.chat_id)
    if not chat_thread.get("success"):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": chat_thread.get("message"), "data": {}})

    response: str = await chat_service.send_message(message_data.message, chat_thread.get("data").get("thread"))

    async def generate():
        # Send chat_id first
        yield f"data: {{'chat_id': '{message_data.chat_id}'}}\n\n"

        # Split response into words and send in chunks of 3
        words = response.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i + 3])
            yield f"data: {{'chunk': '{chunk}'}}\n\n"
            await asyncio.sleep(0.1)  # Small delay between chunks

        # Send done message
        yield f"data: {{'done': true}}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )