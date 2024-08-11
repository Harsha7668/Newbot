#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import time, os
from pyrogram import Client, filters, enums
from config import DOWNLOAD_LOCATION, CAPTION
from main.utils import progress_message, humanbytes

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
            
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import motor.motor_asyncio

# Bot token and database credentials
API_ID = "10811400"
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7412278588:AAHmk19iP3uK79OglBISjicbl70TD6i9wEc"
DATABASE_URI = "your_mongodb_uri"  # Replace with your MongoDB URI
DATABASE_NAME = "your_database_name"  # Replace with your database name

app = Client("python_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)



# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hi! I'm your Python bot. Here's what you can do:\n"
                        "- Upload a Python (.py) or text (.txt) file to store it.\n"
                        "- Use inline buttons to run or delete the file.\n"
                        "- Send a `requirements.txt` file to install dependencies automatically.\n"
                        "What would you like to do?")

# Handle file uploads
@app.on_message(filters.document)
async def handle_document(client, message):
    file_name = message.document.file_name
    if file_name.endswith(('.py', '.txt', 'requirements.txt')):
        file_id = message.document.file_id

        # Save file information to the database
        await db.add_file(file_name, file_id)
        
        # If it's a requirements.txt file, install dependencies without inline buttons
        if file_name == 'requirements.txt':
            file_path = await message.download(file_name=file_name)
            os.system(f"pip install -r {file_path}")
            await message.reply(f"Dependencies installed from '{file_name}'. Now, you can run your Python script.")
        else:
            # Create inline buttons for .py and .txt files
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Run", callback_data=f"run_{file_name}")],
                [InlineKeyboardButton("Delete", callback_data=f"delete_{file_name}")]
            ])
            
            await message.reply(f"File '{file_name}' received and saved.", reply_markup=keyboard)
    else:
        await message.reply("Please upload a valid '.py', '.txt', or 'requirements.txt' file.")

# Handle button callbacks
@app.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data
    file_action, file_name = data.split("_", 1)
    
    file_id = await db.get_file(file_name)
    if not file_id:
        await callback_query.message.reply("The file was not found.")
        return

    if file_action == "run":
        # Run the file using its file_id
        file = await app.get_messages(callback_query.message.chat.id, file_id)
        file_path = await file.download(file_name=file_name)
        output = os.popen(f"python {file_path}").read()
        await callback_query.message.reply(f"Output:\n{output}")

    elif file_action == "delete":
        # Delete the file using its file_id
        await db.delete_file(file_name)
        await app.delete_messages(callback_query.message.chat.id, file_id)
        await callback_query.message.reply(f"File '{file_name}' deleted.")
        await callback_query.message.delete()  # Remove the inline buttons message

@app.on_message(filters.command("myfiles"))
async def list_files(client, message):
    files = await db.list_files()
    if files:
        file_list = "\n".join([f"{file['file_name']}: {file['file_id']}" for file in files])
        await message.reply(f"My Python Files:\n{file_list}")
    else:
        await message.reply("No files uploaded.")

