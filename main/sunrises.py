#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import time, os
from pyrogram import Client, filters, enums
from config import DOWNLOAD_LOCATION, CAPTION
from main.utils import progress_message, humanbytes

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
            
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os

# In-memory file storage
files = {}



# Directory for storing files
DEPOLY = "/depoly"
if not os.path.exists(DEPOLY):
    os.makedirs(DEPOLY)

# Dictionary to store file_name: file_id pairs
files = {}

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
    if message.document.file_name.endswith(('.py', '.txt', 'requirements.txt')):
        if len(files) < 3 or message.document.file_name == 'requirements.txt':
            file_id = message.document.file_id
            file_name = os.path.join(DEPOLY, message.document.file_name)
            files[file_name] = file_id
            await message.download(file_name=file_name)
            
            # Create inline buttons
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Run", callback_data=f"run_{file_name}")],
                [InlineKeyboardButton("Delete", callback_data=f"delete_{file_name}")]
            ])
            
            await message.reply(f"File '{file_name}' received and saved. You now have {len(files)} file(s).", reply_markup=keyboard)
            
            # Automatically install requirements if it's a requirements.txt file
            if file_name.endswith('requirements.txt'):
                os.system(f"pip install -r {file_name}")
                await message.reply(f"Dependencies installed from '{file_name}'. Now, you can run your Python script.")
        else:
            await message.reply("You can only upload and manage up to 3 files, excluding 'requirements.txt'. Please delete a file before uploading a new one.")
    else:
        await message.reply("Please upload a valid '.py', '.txt', or 'requirements.txt' file.")

# Handle button callbacks
@app.on_callback_query()
async def handle_button(client, callback_query):
    data = callback_query.data
    file_action, file_name = data.split("_", 1)
    file_path = os.path.join(DEPOLY, file_name)
    
    if file_action == "run":
        if os.path.exists(file_path):
            output = os.popen(f"python {file_path}").read()
            await callback_query.message.reply(f"Output:\n{output}")
        else:
            await callback_query.message.reply("The file was not found.")
    
    elif file_action == "delete":
        if os.path.exists(file_path):
            os.remove(file_path)
            files.pop(file_path, None)
            await callback_query.message.reply(f"File '{file_name}' deleted.")
            await callback_query.message.delete()  # Remove the inline buttons message
        else:
            await callback_query.message.reply("The file was not found.")

@app.on_message(filters.command("myfiles"))
async def list_files(client, message):
    if files:
        file_list = "\n".join([f"{os.path.basename(name)}: {files[name]}" for name in files])
        await message.reply(f"My Python Files:\n{file_list}")
    else:
        await message.reply("No files uploaded.")

