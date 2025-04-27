import datetime
import os
import traceback
import sys
import uuid

from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from repository.context_repository import ContextRepository
from util.logger import get_logger
from util.prompt_generator import PromptGenerator

from starlette.concurrency import run_in_threadpool
from google import genai

class ChatService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = PromptGenerator()

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._context_repository = ContextRepository()
        except Exception as e:
            self._logger.error(f"Error initializing RagService: {e}")


    async def _update_chat_thread(
            self,
            chat_thread: ChatThreadModel
    ) -> bool:
        is_updated: bool

        chat_thread.updated_at = datetime.datetime.now().isoformat()
        self._logger.info(f"Updating chat thread: {chat_thread.chat_id}")
        is_updated = await self._context_repository.update_one(chat_thread)

        return is_updated

    async def send_message(
            self,
            query: str,
            chat_thread: ChatThreadModel
    ) -> str:
        # Create a new message model and append it to the chat thread
        message_model: MessageModel = MessageModel(
            created_at=datetime.datetime.now().isoformat(),
            role="user",
            content=query.encode("utf-8", errors="replace").decode("utf-8")
        )
        chat_thread.history.append(message_model)
        chat_thread.updated_at = datetime.datetime.now().isoformat()

        prompt: str = self._prompt_generator.generate_main_prompt(user_query=query)
        response: any
        try:
            contents: list = [f"role + {msg.role}, content: {msg.content}" for msg in chat_thread.history[-50:]]
            contents.append(prompt)
            #self._logger.info(f"Contents: {contents}")
            response = self._gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents
            )

        except Exception as e:
            self._logger.error(f"Error generating response: {e}")
            return "I am unable to generate a response at this time."

        chat_thread.history.append(MessageModel(
            created_at=datetime.datetime.now().isoformat(),
            role="ai",
            content=response.text.encode("utf-8", errors="replace").decode("utf-8")
        ))
        is_updated: bool = await self._context_repository.update_one(chat_thread)
        return response.text

chat_service = ChatService()