import asyncio
import datetime
import uuid

from repository.context_repository import context_repository
from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel
from service.chat_service import chat_service


async def main():
    print("Welcome to the Psychological Support Chat Test")
    print("=============================================")

    # Create or load a chat thread
    choice = input("Would you like to (1) Create a new chat or (2) Load an existing one? ")

    chat_thread = None
    if choice == "1":
        chat_name = input("Enter a name for this chat session: ")
        chat_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()

        chat_thread = ChatThreadModel(
            chat_id=chat_id,
            chat_name=chat_name,
            created_at=now,
            updated_at=now,
            history=[]
        )

        # Save the new chat thread to the database
        await context_repository.insert_one(chat_thread)
        print(f"New chat created with ID: {chat_id}")

    elif choice == "2":
        # List available chats
        all_chats = await context_repository.get_all()

        if not all_chats:
            print("No existing chats found. Creating a new one.")
            chat_name = input("Enter a name for this chat session: ")
            chat_id = str(uuid.uuid4())
            now = datetime.datetime.now().isoformat()

            chat_thread = ChatThreadModel(
                chat_id=chat_id,
                chat_name=chat_name,
                created_at=now,
                updated_at=now,
                history=[]
            )

            # Save the new chat thread to the database
            await context_repository.insert_one(chat_thread)
            print(f"New chat created with ID: {chat_id}")
        else:
            print("Available chats:")
            for i, chat in enumerate(all_chats):
                print(f"{i + 1}. {chat.chat_name} (ID: {chat.chat_id})")

            chat_index = int(input("Enter the number of the chat you want to load: ")) - 1
            if 0 <= chat_index < len(all_chats):
                chat_thread = all_chats[chat_index]
            else:
                print("Invalid selection. Creating a new chat.")
                chat_name = input("Enter a name for this chat session: ")
                chat_id = str(uuid.uuid4())
                now = datetime.datetime.now().isoformat()

                chat_thread = ChatThreadModel(
                    chat_id=chat_id,
                    chat_name=chat_name,
                    created_at=now,
                    updated_at=now,
                    history=[]
                )

                # Save the new chat thread to the database
                await context_repository.insert_one(chat_thread)
    else:
        print("Invalid choice. Exiting.")
        return

    # Start the chat loop
    print("\nChat session started. Type 'exit' to end the conversation.\n")

    # Display chat history if any exists
    if chat_thread.history:
        print("Previous messages:")
        for msg in chat_thread.history:
            role_display = "You" if msg.role == "user" else "Assistant"
            print(f"{role_display}: {msg.content}")
        print("\n" + "-" * 50 + "\n")

    # Chat loop
    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break

        print("Assistant is typing...")
        response = await chat_service.send_message(user_input, chat_thread)
        print(f"Assistant: {response}")
        print()


if __name__ == "__main__":
    asyncio.run(main())