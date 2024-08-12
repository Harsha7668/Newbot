from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from Database.database import db


@Client.on_message(filters.command("start"))
async def start(self, message):
    await message.reply("Hi! I'm your Python bot. Here's what you can do:\n"
                        "- Upload a Python (.py) or text (.txt) file to store it.\n"
                        "- Send a plain text message to convert it into a .py file.\n"
                        "- Use inline buttons to run or delete the file.\n"
                        "- Send a `requirements.txt` file to install dependencies automatically.\n"
                        "What would you like to do?")


@Client.on_message(filters.document)
async def handle_document(self, message):
    file_name = message.document.file_name
    if file_name.endswith(('.py', '.txt', 'requirements.txt')):
        file_id = message.document.file_id
        # Save the file information to the database
        await db.save_file(file_name, file_id, message.from_user.id)

        await message.download(file_name=file_name)

        if file_name == 'requirements.txt':
            # Save user-specific requirements and install dependencies
            with open(file_name, 'r') as file:
                content = file.read()
                await db.save_requirements(message.from_user.id, content)
            os.system(f"pip install -r {file_name}")
            await message.reply(f"Dependencies installed from '{file_name}'. Your custom `requirements.txt` has been saved.")
        else:
            # Create inline buttons for .py and .txt files
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Run", callback_data=f"run_{file_name}")],
                [InlineKeyboardButton("Delete", callback_data=f"delete_{file_name}")]
            ])
            await message.reply(f"File '{file_name}' received and saved.", reply_markup=keyboard)
    else:
        await message.reply("Please upload a valid '.py', '.txt', or 'requirements.txt' file.")


@Client.on_message(filters.text)
async def handle_text(self, message):
    # Create a .py file from the text message
    file_name = f"{message.from_user.id}_{message.message_id}.py"
    with open(file_name, 'w') as f:
        f.write(message.text)

    # Save the file information to the database
    await db.save_file(file_name, None, message.from_user.id)

    # Create inline buttons for the .py file
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Run", callback_data=f"run_{file_name}")],
        [InlineKeyboardButton("Delete", callback_data=f"delete_{file_name}")]
    ])
    await message.reply(f"Text converted to '{file_name}' and saved as a Python script.", reply_markup=keyboard)


@Client.on_callback_query()
async def handle_button(self, callback_query):
    data = callback_query.data
    file_action, file_name = data.split("_", 1)

    if file_action == "run":
        output = os.popen(f"python {file_name}").read()
        await callback_query.message.reply(f"Output:\n{output}")

    elif file_action == "delete":
        await db.delete_file(file_name, callback_query.from_user.id)
        os.remove(file_name)
        await callback_query.message.reply(f"File '{file_name}' deleted.")
        await callback_query.message.delete()  # Remove the inline buttons message


@Client.on_message(filters.command("myfiles"))
async def list_files(self, message):
    files = await db.get_user_files(message.from_user.id)
    if files:
        file_list = "\n".join([f"{file.get('file_name', 'Unnamed File')}: {file.get('file_id', 'No ID')}" for file in files])
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(file.get('file_name'), callback_data=f"run_{file.get('file_name')}")] for file in files])
        await message.reply(f"My Python Files:\n{file_list}", reply_markup=keyboard)
    else:
        await message.reply("No files uploaded.")


@Client.on_message(filters.command("myrequirements"))
async def list_requirements(self, message):
    user_data = await db.get_user_requirements(message.from_user.id)
    if user_data and "requirements" in user_data:
        await message.reply(f"Your saved `requirements.txt`:\n\n{user_data['requirements']}")
    else:
        await message.reply("You have not uploaded a `requirements.txt` file yet.")
