import motor.motor_asyncio
from config import DATABASE_NAME, DATABASE_URI


# Initialize the database instance
class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.files_col = self.db["files"]          # Collection for storing file metadata
        self.file_data_col = self.db["file_data"]  # Collection for storing additional file data

    async def add_file(self, file_name, file_id):
        await self.files_col.update_one({"file_name": file_name}, {"$set": {"file_id": file_id}}, upsert=True)

    async def get_file(self, file_name):
        doc = await self.files_col.find_one({"file_name": file_name})
        return doc['file_id'] if doc else None

    async def delete_file(self, file_name):
        await self.files_col.delete_one({"file_name": file_name})
        await self.file_data_col.delete_one({"file_name": file_name})  # Ensure related data is also removed

    async def list_files(self):
        return await self.files_col.find().to_list(length=100)  # Retrieve up to 100 files

db = Database(DATABASE_URI, DATABASE_NAME)
