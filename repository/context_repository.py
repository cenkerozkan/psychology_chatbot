import asyncio

from base.mongodb_repository_base import MongoDBRepositoryBase
from util.logger import get_logger
from db.mongodb_connector import MongoDBConnector
from db.model.chat_thread_model import ChatThreadModel
from db.model.message_model import MessageModel

class ContextRepository(MongoDBRepositoryBase):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._db = MongoDBConnector().client["psychology_chat_context"]
        self._collection = self._db["chat_history"]

    # Ensure database setup
    async def _ensure_db_setup(self):
        try:
            # List all databases
            db_list = await self._db.client.list_database_names()

            # Check if our database exists
            if "psychology_chat_context" not in db_list:
                # Create database by inserting a dummy document and then deleting it
                await self._db.command({
                    "create": "chat_history"})
                self._logger.info("Created context database")

            # Check if collection exists
            collections = await self._db.list_collection_names()
            if "chat_history" not in collections:
                await self._db.create_collection(
                    "chat_history")
                self._logger.info("Created chat_history collection")

            # Create index after ensuring collection exists
            await self._collection.create_index("chat_id", unique=True)
            self._logger.info("Created index on chat_id")

            self._logger.info("Database setup completed successfully")
        except Exception as e:
            self._logger.error(f"Database setup error: {e}")
            raise Exception(f"Failed to setup database: {e}")

    async def insert_one(
            self,
            document: ChatThreadModel
    ) -> bool:
        self._logger.info(f"Inserting document: {document}")
        try:
            await self._collection.insert_one(document.model_dump())

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)
        return True

    async def insert_many(
            self,
            documents: list[ChatThreadModel]
    ) -> bool:
        self._logger.info(f"Inserting documents: {documents}")
        try:
            await self._collection.insert_many([doc.model_dump() for doc in documents])

        except Exception as e:
            print(e)
            raise Exception(e)
        return True

    async def get_one_by_id(
            self,
            id: str
    ) -> ChatThreadModel | None:
        result: any
        self._logger.info(f"Retrieving document with id: {id}")
        try:
            result = await self._collection.find_one({"chat_id": id})
        except Exception as e:
            self._logger.error(f"Something went wrong: {e}")
            return None
        return ChatThreadModel(**result) if result else None

    async def get_one_by_name(
            self,
            name: str
    ) -> ChatThreadModel | None:
        result: any
        self._logger.info(f"Retrieving document with name: {name}")
        try:
            result = await self._collection.find_one({"chat_name": name})

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)
        return ChatThreadModel(**result) if result else None

    async def get_all(self) -> list[ChatThreadModel] | None:
        results: any
        try:
            results = self._collection.find()

        except Exception as e:
            self._logger.error(e)
            raise Exception(e)

        return [ChatThreadModel(**result) async for result in results]

    async def update_one(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        result: bool = False
        try:
            await self._collection.update_one({"chat_id": chat_history.chat_id}, {"$set": chat_history.model_dump()})
            result = True
        except Exception as e:
            self._logger.error(f"Failed to update document with id: {chat_history.chat_id}, error: {e}")
        return result

    async def update_many(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        return False

    async def delete_one(
            self,
            chat_history: ChatThreadModel
    ) -> bool:
        result: bool = False
        try:
            await self._collection.delete_one({"chat_id": chat_history.chat_id})
            result = True
        except Exception as e:
            self._logger.error(e)
            raise Exception(e)
        return result

    async def delete_one_by_id(
            self,
            id: str
    ) -> bool:
        try:
            result = await self._collection.delete_one({"chat_id": id})
        except Exception as e:
            self._logger.error(e)
            return False
        if result.deleted_count == 1:
            return True
        else:
            return False

    async def delete_many_by_id(
            self,
            ids
    ) -> bool:
        try:
            result = await self._collection.delete_many({"chat_id": {"$in": ids}})
        except Exception as e:
            self._logger.error(e)
            raise Exception(e)

        if result.deleted_count > 0:
            return True
        else:
            return False

    async def get_all_by_uid(
            self,
            uid: str
    ) -> list[ChatThreadModel] | None:
        results: any
        try:
            results = self._collection.find({"user_uid": uid})
        except Exception as e:
            self._logger.error(f"Something went wrong: {e}")
            return None
        return [ChatThreadModel(**result) async for result in results]

    async def get_one_by_uid(
            self,
            uid: str
    ) -> ChatThreadModel | None:
        result: any
        try:
            result = await self._collection.find_one({"user_uid": uid})
        except Exception as e:
            self._logger.error(f"Something went wrong: {e}")
            return None
        return ChatThreadModel(**result) if result else None

    async def get_history_by_id(
            self,
            id: str
    ) -> list[MessageModel] | None:
        result: any
        try:
            result = await self._collection.find_one({"chat_id": id})
        except Exception as e:
            self._logger.error(f"Something went wrong: {e}")
            return None
        return [MessageModel(**message) for message in result.get("history")] if result else []

context_repository = ContextRepository()