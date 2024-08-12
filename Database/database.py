
import motor.motor_asyncio
from config import DATABASE_NAME, DATABASE_URI


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.files_col = self.db["files"]  # Collection for storing file metadata
        self.file_data_col = self.db["file_data"]  # Collection for storing additional file data
        self.user_requirements_col = self.db["user_requirements"]  # Collection for storing user requirements

    async def save_file(self, file_name, file_id, user_id):
        await self.files_col.insert_one({"file_name": file_name, "file_id": file_id, "user_id": user_id})

    async def delete_file(self, file_name, user_id):
        await self.files_col.delete_one({"file_name": file_name, "user_id": user_id})

    async def get_user_files(self, user_id):
        return await self.files_col.find({"user_id": user_id}).to_list(None)

    async def save_requirements(self, user_id, content):
        await self.user_requirements_col.update_one(
            {"user_id": user_id},
            {"$set": {"requirements": content}},
            upsert=True
        )

    async def get_user_requirements(self, user_id):
        return await self.user_requirements_col.find_one({"user_id": user_id})

# Initialize the database instance
db = Database(DATABASE_URI, DATABASE_NAME)
