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
from openai import AsyncOpenAI


class ChatService:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._prompt_generator = PromptGenerator()

        try:
            self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            self._openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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

    async def get_one_chat(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        # Retrieve the chat thread by ID
        chat_thread: ChatThreadModel = await self._context_repository.get_one_by_id(chat_id)
        if chat_thread is None:
            self._logger.error(f"Failed to retrieve chat thread: {chat_id}")
            result.update({"code": 404, "success": False, "message": "Chat not found."})
            return result
        else:
            result.update({"code": 200, "success": True, "message": "Chat thread retrieved successfully.",
                           "data": {"thread": chat_thread}})
        return result

    async def create_chat_thread(
            self,
            user_uid: str,
            chat_name: str,
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        # First create a new chat thread object.
        new_chat_thread: ChatThreadModel = ChatThreadModel(
            user_uid=user_uid,
            chat_name=chat_name,
            chat_id=str(uuid.uuid4()),
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat(),
            history=[]
        )
        # Save the new chat thread to the database
        is_inserted: bool = await self._context_repository.insert_one(new_chat_thread)
        if not is_inserted:
            self._logger.error(f"Failed to create chat thread for user: {user_uid}")
            result.update({"code": 500, "success": False, "message": "Something went wrong creating chat."})
        result.update({"code": 200, "success": True, "message": "Chat thread created successfully.",
                       "data": new_chat_thread.model_dump()})
        return result

    async def get_all_chats(
            self,
            user_uid: str
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        # Retrieve all chat threads for the user
        chat_threads: list[ChatThreadModel] = await self._context_repository.get_all_by_uid(user_uid)
        if chat_threads is None:
            self._logger.error(f"Failed to retrieve chat threads for user: {user_uid}")
            result.update({"code": 500, "success": False, "message": "Something went wrong retrieving chats."})
        else:
            refined_results: list = []
            if len(chat_threads) != 0:
                for i in chat_threads:
                    _: dict = i.model_dump()
                    _.pop("history")
                    refined_results.append(_)

            result.update({"code": 200, "success": True, "message": "Chat threads retrieved successfully.",
                           "data": {"threads": [chat_thread for chat_thread in refined_results]}})
        return result

    async def get_chat_history(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        chat_results: list[MessageModel] = await self._context_repository.get_history_by_id(chat_id)
        if chat_results is None:
            self._logger.error(f"Failed to retrieve chat history for chat: {chat_id}")
            result.update({"code": 500, "success": False, "message": "Something went wrong retrieving chat history."})
            return result
        else:
            refined_results: list = []
            if len(chat_results) != 0:
                for i in chat_results:
                    _: dict = i.model_dump()
                    refined_results.append(_)
            result.update({"code": 200, "success": True, "message": "Chat history retrieved successfully.",
                           "data": {"history": [message for message in refined_results]}})
        return result

    async def delete_chat_thread(
            self,
            chat_id: str
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        # Delete the chat thread from the database
        is_deleted: bool = await self._context_repository.delete_one_by_id(chat_id)
        if not is_deleted:
            self._logger.error(f"Failed to delete chat thread: {chat_id}")
            result.update({"code": 500, "success": False, "message": "Something went wrong deleting chat."})
        else:
            result.update({"code": 200, "success": True, "message": "Chat thread deleted successfully."})
        return result

    async def update_chat_name(
            self,
            chat_id: str,
            chat_name: str
    ) -> dict:
        result: dict = {"code": 0, "success": False, "message": "", "data": {}}
        # Retrieve the chat thread
        chat_thread: ChatThreadModel = await self._context_repository.get_one_by_id(chat_id)
        if chat_thread is None:
            self._logger.error(f"Failed to retrieve chat thread: {chat_id}")
            result.update({"code": 500, "success": False, "message": "Something went wrong retrieving chat."})
            return result
        # Update the chat name
        chat_thread.chat_name = chat_name
        is_updated: bool = await self._update_chat_thread(chat_thread)
        if not is_updated:
            self._logger.error(f"Failed to update chat name for chat: {chat_id}")
            result.update({"code": 500, "success": False, "message": "Something went wrong updating chat name."})
        else:
            result.update({"code": 200, "success": True, "message": "Chat name updated successfully."})
        return result

    async def _try_openai_fallback(self, contents: list) -> str:
        """Fallback method to use OpenAI when Gemini fails"""
        try:
            # Convert the contents to OpenAI message format
            messages = []
            for content in contents[:-1]:  # Exclude the last prompt
                parts = content.split('\n', 1)
                if len(parts) == 2:
                    role = parts[0].replace('role: ', '')
                    content = parts[1].replace('content: ', '')
                    # Map 'ai' role to 'assistant' for OpenAI
                    role = 'assistant' if role == 'ai' else role
                    messages.append({"role": role, "content": content})

            # Add the system prompt
            messages.append({"role": "system", "content": contents[-1]})

            response = await self._openai_client.chat.completions.create(
                model="gpt-4.1",  # You can adjust the model as needed
                messages=messages
            )
            return response.choices[0].message.content

        except Exception as e:
            self._logger.error(f"Error in OpenAI fallback: {e}")
            return "I am unable to generate a response at this time."

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
        response_text: str = ""

        try:
            contents: list = [f"role: {msg.role}\ncontent: {msg.content}" for msg in chat_thread.history[-400:]]
            contents.append(prompt)

            try:
                # Try Gemini first
                response = self._gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents
                )
                response_text = response.text

            except Exception as gemini_error:
                # Log Gemini error and try OpenAI
                self._logger.warning(f"Gemini API error, falling back to OpenAI: {gemini_error}")
                response_text = await self._try_openai_fallback(contents)

        except Exception as e:
            self._logger.error(f"Error generating response: {e}")
            return "I am unable to generate a response at this time."

        # Add the AI response to chat history
        chat_thread.history.append(MessageModel(
            created_at=datetime.datetime.now().isoformat(),
            role="ai",
            content=response_text.encode("utf-8", errors="replace").decode("utf-8")
        ))

        is_updated: bool = await self._context_repository.update_one(chat_thread)
        return response_text


chat_service = ChatService()