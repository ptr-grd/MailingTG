from pyrogram import Client

api_id = 462746	# Пример
api_hash = "wgwgrwghetjk568k5" # Пример

with Client("main", api_id, api_hash) as app:
    app.send_message("me", "Greetings from **Pyrogram**!")