import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(input("Enter your api_id: "))
API_HASH = input("Enter your api_hash: ")

async def get_session(name):
    print(f"\n--- Logging in for {name} ---")
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        session_string = client.session.save()
        print(f"\n{name} session string (save this!):\n{session_string}\n")

async def main():
    await get_session("Iklass")
    await get_session("Abdul")

asyncio.run(main())
