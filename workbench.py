import asyncio

from repository.context_repository import context_repository
from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel

async def main():
    # Create a ChatThreadModel instance using the Pydantic model
    chat_thread = ChatThreadModel(
        chat_id="12345",
        chat_name="Test Chat",
        created_at="2023-10-01T12:00:00Z",
        updated_at="2023-10-01T12:00:00Z",
        history=[]  # Empty history to start with
    )

    # Insert the new chat thread
    await context_repository.insert_one(chat_thread)

    # Get all chat threads
    all_chats = await context_repository.get_all()
    print(all_chats)

    # Update a chat thread
    chat_thread.chat_name = "Updated Chat"
    await context_repository.update_one(chat_thread)

    # Add a message to history if needed
    message = MessageModel(
        created_at="2023-10-01T12:05:00Z",
        role="user",
        content="Hello, this is a test message"
    )
    chat_thread.history.append(message)
    await context_repository.update_one(chat_thread)

asyncio.run(main())