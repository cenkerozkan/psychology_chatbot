# Psychology Chatbot API

This is the backend API for a psychology-focused chatbot application. It allows users to create chat threads, send messages, retrieve chat history, and manage their chats. The API uses FastAPI and interacts with a MongoDB database to store chat context. It leverages AI models (Gemini with an OpenAI fallback) to generate responses.

## Features

*   **Chat Thread Management:**
    *   Create new chat threads.
    *   Retrieve all chat threads for a user.
    *   Retrieve the history of a specific chat.
    *   Delete chat threads.
    *   Update the name of a chat thread.
*   **Messaging:**
    *   Send messages within a chat thread.
    *   Receives responses from an AI model (Gemini or OpenAI).
    *   Supports streaming responses for a more interactive experience.
*   **API Key Authentication:** Secures API endpoints using an API key.
*   **MongoDB Integration:** Stores chat history and thread information in a MongoDB database.

## Tech Stack

*   **Framework:** FastAPI
*   **Database:** MongoDB
*   **AI Models:** Google Gemini (with fallback to OpenAI GPT-4.1)
*   **Language:** Python
*   **Deployment:** Heroku

## API Endpoints

The base URL for this API is: `https://psychology-chatbot-1867c6f2e005.herokuapp.com/`

All endpoints require an `X-API-Key` header for authentication.

---

### 1. Create Chat Thread

*   **Method:** `POST`
*   **Endpoint:** `/api/chat/create_chat_thread`
*   **Description:** Creates a new chat thread.
*   **Headers:**
    *   `X-API-Key`: Your API Key
    *   `Content-Type`: `application/json`
*   **Request Body (JSON):**
    ```json
    {
        "user_uid": "string",
        "chat_name": "string"
    }
    ```
*   **Responses:**
    *   **200 OK (Success):**
        ```json
        {
            "success": true,
            "message": "Chat thread created successfully.",
            "data": {
                "user_uid": "user123",
                "chat_name": "My First Chat",
                "chat_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "created_at": "2025-05-17T14:30:00.000Z",
                "updated_at": "2025-05-17T14:30:00.000Z",
                "history": []
            }
        }
        ```
    *   **401 Unauthorized (Invalid API Key):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **500 Internal Server Error (Creation Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong creating chat.",
            "data": {}
        }
        ```

---

### 2. Get All Chats for User

*   **Method:** `GET`
*   **Endpoint:** `/api/chat/get_all_chats/{user_uid}`
*   **Description:** Retrieves all chat threads for a specific user.
*   **Headers:**
    *   `X-API-Key`: Your API Key
*   **Path Parameters:**
    *   `user_uid` (string): The unique identifier of the user.
*   **Responses:**
    *   **200 OK (Success):**
        ```json
        {
            "success": true,
            "message": "Chat threads retrieved successfully.",
            "data": {
                "threads": [
                    {
                        "user_uid": "user123",
                        "chat_name": "My First Chat",
                        "chat_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                        "created_at": "2025-05-17T14:30:00.000Z",
                        "updated_at": "2025-05-17T14:35:00.000Z"
                    },
                    {
                        "user_uid": "user123",
                        "chat_name": "Another Conversation",
                        "chat_id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
                        "created_at": "2025-05-17T15:00:00.000Z",
                        "updated_at": "2025-05-17T15:05:00.000Z"
                    }
                ]
            }
        }
        ```
    *   **200 OK (Success - No chats found):**
        ```json
        {
            "success": true,
            "message": "Chat threads retrieved successfully.",
            "data": {
                "threads": []
            }
        }
        ```
    *   **401 Unauthorized (Invalid API Key):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **500 Internal Server Error (Retrieval Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong retrieving chats.",
            "data": {}
        }
        ```

---

### 3. Get Chat History

*   **Method:** `GET`
*   **Endpoint:** `/api/chat/get_chat_history/{chat_id}`
*   **Description:** Retrieves the message history for a specific chat thread.
*   **Headers:**
    *   `X-API-Key`: Your API Key
*   **Path Parameters:**
    *   `chat_id` (string): The unique identifier of the chat thread.
*   **Responses:**
    *   **200 OK (Success):**
        ```json
        {
            "success": true,
            "message": "Chat history retrieved successfully.",
            "data": {
                "history": [
                    {
                        "created_at": "2025-05-17T14:30:05.000Z",
                        "role": "user",
                        "content": "Hello there!"
                    },
                    {
                        "created_at": "2025-05-17T14:30:10.000Z",
                        "role": "ai",
                        "content": "Hi! How can I help you today?"
                    }
                ]
            }
        }
        ```
    *   **200 OK (Success - Empty history):**
        ```json
        {
            "success": true,
            "message": "Chat history retrieved successfully.",
            "data": {
                "history": []
            }
        }
        ```
    *   **401 Unauthorized (Invalid API Key):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **500 Internal Server Error (Retrieval Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong retrieving chat history.",
            "data": {}
        }
        ```

---

### 4. Delete Chat Thread

*   **Method:** `DELETE`
*   **Endpoint:** `/api/chat/delete_chat_thread/{chat_id}`
*   **Description:** Deletes a specific chat thread.
*   **Headers:**
    *   `X-API-Key`: Your API Key
*   **Path Parameters:**
    *   `chat_id` (string): The unique identifier of the chat thread to delete.
*   **Responses:**
    *   **200 OK (Success):**
        ```json
        {
            "success": true,
            "message": "Chat thread deleted successfully.",
            "data": {}
        }
        ```
    *   **401 Unauthorized (Invalid API Key):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **500 Internal Server Error (Deletion Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong deleting chat.",
            "data": {}
        }
        ```
        *(This can also occur if the chat_id does not exist)*

---

### 5. Update Chat Name

*   **Method:** `PATCH`
*   **Endpoint:** `/api/chat/update_chat_name/{chat_id}/{new_chat_name}`
*   **Description:** Updates the name of a specific chat thread.
*   **Headers:**
    *   `X-API-Key`: Your API Key
*   **Path Parameters:**
    *   `chat_id` (string): The unique identifier of the chat thread.
    *   `new_chat_name` (string): The new name for the chat thread.
*   **Responses:**
    *   **200 OK (Success):**
        ```json
        {
            "success": true,
            "message": "Chat name updated successfully.",
            "data": {}
        }
        ```
    *   **401 Unauthorized (Invalid API Key):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **500 Internal Server Error (Chat Retrieval Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong retrieving chat.",
            "data": {}
        }
        ```
        *(This can occur if the chat_id does not exist)*
    *   **500 Internal Server Error (Update Failed):**
        ```json
        {
            "success": false,
            "message": "Something went wrong updating chat name.",
            "data": {}
        }
        ```

---

### 6. Send Message

*   **Method:** `POST`
*   **Endpoint:** `/api/chat/send_message`
*   **Description:** Sends a message within a chat thread and receives a streaming AI response.
*   **Headers:**
    *   `X-API-Key`: Your API Key
    *   `Content-Type`: `application/json`
*   **Request Body (JSON):**
    ```json
    {
        "chat_id": "string",
        "message": "string"
    }
    ```
*   **Responses:**
    *   **200 OK (Success - Streaming Response):**
        The response is of `media_type="text/event-stream"`.
        Events are sent in the format `data: <json_string>\n\n`.
        Example stream:
        ```text
        data: {"chat_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"}

        data: {"chunk": "This is the "}

        data: {"chunk": "first part of the AI response."}

        data: {"chunk": " And this is more."}

        data: {"done": true}
        ```
        If the AI fails to generate a response, the chunks might contain an error message like "I am unable to generate a response at this time." but the stream will still complete with `{"done": true}`.

    *   **401 Unauthorized (Invalid API Key - JSON Response):**
        ```json
        {
            "success": false,
            "message": "Invalid API key",
            "data": {}
        }
        ```
    *   **404 Not Found (Chat ID Not Found - JSON Response):**
        ```json
        {
            "success": false,
            "message": "Chat not found.",
            "data": {}
        }
        ```

## How to Use

1.  **Obtain an API Key:** You will need a valid API key to interact with the endpoints. The `API_KEY` is set as an environment variable on the server (defaulting to `default-dev-key` for development).
2.  **Set the `X-API-Key` Header:** Include your API key in the `X-API-Key` header for all requests.
3.  **Interact with Endpoints:**
    *   Start by creating a chat thread using `POST /api/chat/create_chat_thread`.
    *   Use the `chat_id` returned to send messages via `POST /api/chat/send_message`.
    *   Retrieve your chat history or all your chats using the respective GET endpoints.

**Example: Creating a chat thread with cURL**

```bash
curl -X POST "https://psychology-chatbot-1867c6f2e005.herokuapp.com/api/chat/create_chat_thread" \
     -H "X-API-Key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "user_uid": "user123",
           "chat_name": "My First Chat"
         }'
```

**Example: Sending a message with cURL**

```bash
# Use --no-buffer or equivalent with curl to see the streaming response progressively
curl --no-buffer -X POST "https://psychology-chatbot-1867c6f2e005.herokuapp.com/api/chat/send_message" \
     -H "X-API-Key: YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "chat_id": "your_chat_id_from_previous_step",
           "message": "Hello, chatbot!"
         }'
```

## Project Structure

```
psychologyChatbot/
├── repository/
│   └── context_repository.py  # Handles MongoDB interactions for chat context
├── routes/
│   └── chat_service_route.py  # Defines API endpoints using FastAPI
└── service/
    └── chat_service.py        # Contains business logic for chat operations and AI interaction
```

## Environment Variables

The application relies on the following environment variables:

*   `API_KEY`: The API key for securing the API endpoints. (e.g., `default-dev-key`)
*   `GEMINI_API_KEY`: API key for Google Gemini.
*   `OPENAI_API_KEY`: API key for OpenAI.
*   MongoDB connection details (implicitly handled by `MongoDBConnector`, ensure your environment is configured for it).
```