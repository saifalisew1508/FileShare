import os
import socket

import dotenv
import heroku3
import urllib3
from bot import Bot
from config import ADMINS, HEROKU_API_KEY, HEROKU_APP_NAME
from pyrogram import filters
from pyrogram.types import Message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    heroku = heroku3.from_key(HEROKU_API_KEY)
    app = heroku.app(HEROKU_APP_NAME)
    heroku_config = app.config()
else:
    app = None

forbidden_characters = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]

async def is_heroku():
    return "heroku" in socket.getfqdn()

@Bot.on_message(filters.command("getvar") & filters.user(ADMINS))
async def get_var(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/getvar [Var Name]")
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if app is None:
            return await message.reply_text(
                "Make sure your HEROKU_API_KEY and HEROKU_APP_NAME are configured correctly in Heroku config vars."
            )
        heroku_config = app.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"<b>{check_var}:</b> <code>{heroku_config[check_var]}</code>"
            )
        else:
            return await message.reply_text(f"Unable to find variable {check_var}")
    else:
        path = dotenv.find_dotenv("config.env")
        if not path:
            return await message.reply_text(".env file not found.")
        output = dotenv.get_key(path, check_var)
        if not output:
            await message.reply_text(f"Unable to find variable {check_var}")
        else:
            return await message.reply_text(
                f"<b>{check_var}:</b> <code>{str(output)}</code>"
            )

@Bot.on_message(filters.command("delvar") & filters.user(ADMINS))
async def del_var(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/delvar [Var Name]")
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if app is None:
            return await message.reply_text(
                "Make sure your HEROKU_API_KEY and HEROKU_APP_NAME are configured correctly in Heroku config vars."
            )
        heroku_config = app.config()
        if check_var in heroku_config:
            await message.reply_text(f"Successfully deleted variable {check_var}")
            del heroku_config[check_var]
        else:
            return await message.reply_text(f"Unable to find variable {check_var}")
    else:
        path = dotenv.find_dotenv("config.env")
        if not path:
            return await message.reply_text(".env file not found.")
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text(f"Unable to find variable {check_var}")
        else:
            await message.reply_text(f"Successfully deleted variable {check_var}")
            os.system(f"kill -9 {os.getpid()} && bash start")

@Bot.on_message(filters.command("setvar") & filters.user(ADMINS))
async def set_var(client: Bot, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("<b>Usage:</b>\n/setvar [Var Name] [Var Value]")
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if app is None:
            return await message.reply_text(
                "Make sure your HEROKU_API_KEY and HEROKU_APP_NAME are configured correctly in Heroku config vars."
            )
        heroku_config = app.config()
        if to_set in heroku_config:
            await message.reply_text(f"Successfully updated variable {to_set} to {value}")
        else:
            await message.reply_text(
                f"Successfully added variable {to_set} with value {value}"
            )
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv("config.env")
        if not path:
            return await message.reply_text(".env file not found.")
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            await message.reply_text(f"Successfully updated variable {to_set} to {value}")
        else:
            await message.reply_text(
                f"Successfully added variable {to_set} with value {value}"
            )
        os.system(f"kill -9 {os.getpid()} && bash start")
