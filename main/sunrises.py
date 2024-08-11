from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from Database.database import db

@Client.on_message(filters.command("start"))
async def start(self, message):
    await message.reply("Hi! I'm your Python bot. Here's what you can do:\n"
                        "- Upload a Python (.py) or text (.txt) file to store it.\n"
                        "- Use inline buttons to run or delete the file.\n"
                        "- Send a `requirements.txt` file to install dependencies automatically.\n"
                        "What would you like to do?")

@Client.on_message(filters.document)
async def handle_document(self, message):
    file_name = message.document.file_name
    if file_name.endswith(('.py', '.txt', 'requirements.txt')):
        file_id = message.document.file_id
        # Insert file information into the database
        await db.files_col.insert_one({"file_name": file_name, "file_id": file_id})

        await message.download(file_name=file_name)
        
        # If it's a requirements.txt file, install dependencies without inline buttons
        if file_name == 'requirements.txt':
            os.system(f"pip install -r {file_name}")
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

@Client.on_callback_query()
async def handle_button(self, callback_query):
    data = callback_query.data
    file_action, file_name = data.split("_", 1)
    
    if file_action == "run":
        output = os.popen(f"python {file_name}").read()
        await callback_query.message.reply(f"Output:\n{output}")
    
    elif file_action == "delete":
        await db.files_col.delete_one({"file_name": file_name})
        os.remove(file_name)
        await callback_query.message.reply(f"File '{file_name}' deleted.")
        await callback_query.message.delete()  # Remove the inline buttons message

@Client.on_message(filters.command("myfiles"))
async def list_files(self, message):
    files = await db.files_col.find().to_list(None)

    # Debugging: Print the file documents to see their structure
    print("Files from DB:", files)

    if files:
        file_list = "\n".join([f"{file.get('file_name', 'Unnamed File')}: {file.get('file_id', 'No ID')}" for file in files])
        await message.reply(f"My Python Files:\n{file_list}")
    else:
        await message.reply("No files uploaded.")
