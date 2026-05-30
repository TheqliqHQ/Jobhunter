import asyncio
import json
import logging
import os
import random
from datetime import datetime, timedelta

import anthropic
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
IKLASS_SESSION = os.getenv("IKLASS_SESSION")
ABDUL_SESSION = os.getenv("ABDUL_SESSION")
NOTIFY_CHAT_ID = int(os.getenv("NOTIFY_CHAT_ID", "0"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

COOLDOWN_DAYS = 14
STORAGE_TAG = "JOB_HUNTER_CONTACTED_V1"

TARGET_GROUPS = [
    -1001854701169,  # PrimeClubOFM
    -1001891392293,  # ofmjobs
    -1002501290895,  # ofmpros
]

SKILL_KEYWORDS = [
    "AI content", "AI model", "Kling AI", "Kling", "CapCut",
    "Nano Banana", "Freepik", "Wavespeed", "Higgsfield", "Comfy UI",
    "content creator", "content operator", "video editing",
    "visual storytelling", "AI tools", "creative",
]

IKLASS_VARIANTS = [
    """Hey! Just saw your post about the AI content operator role. I've got 2 years doing similar work with Kling and other tools. Keen to apply if you're still hiring.

Cheers,
Iklass""",
    """Hi! Interested in the AI content role. I've got solid 2 years experience with Kling AI and video editing. Would love to chat about this opportunity.

Talk soon,
Iklass""",
    """Just came across your hiring post. I've been creating AI content for 2 years now, pretty familiar with Kling and similar tools. Let's see if we're a good fit!

Iklass""",
]

ABDUL_VARIANTS = [
    """Hey! Saw your posting for the content creator role. Been in the AI content space for 2 years, comfortable with Kling and video editing. Interested!

Cheers,
Abdul""",
    """Hi there! Your AI content role caught my attention. 2 years experience with video creation and AI tools. Would be great to discuss further.

Best,
Abdul""",
    """Just found your job post. I'm a content creator with 2 years in the AI space, familiar with Kling and the whole workflow. Let's connect!

Abdul""",
]

# In-memory store: poster_id -> {"first_contact": datetime, "iklass": bool, "abdul": bool}
contacted_employers: dict[int, dict] = {}
storage_msg_id: int | None = None


async def load_contacted(client):
    """Load contacted employers from Iklass's Saved Messages."""
    global contacted_employers, storage_msg_id
    try:
        async for msg in client.iter_messages("me", limit=100):
            if msg.text and msg.text.startswith(STORAGE_TAG):
                raw = json.loads(msg.text[len(STORAGE_TAG) + 1:])
                contacted_employers = {
                    int(k): {
                        "first_contact": datetime.fromisoformat(v["first_contact"]),
                        "iklass": v.get("iklass", False),
                        "abdul": v.get("abdul", False),
                    }
                    for k, v in raw.items()
                }
                storage_msg_id = msg.id
                logger.info(f"Loaded {len(contacted_employers)} contacted employers from Telegram")
                return
    except Exception as e:
        logger.error(f"Failed to load contacted employers: {e}")
    logger.info("No existing contacted employers found — starting fresh")


async def save_contacted(client):
    """Save contacted employers to Iklass's Saved Messages."""
    global storage_msg_id
    try:
        raw = {
            str(k): {
                "first_contact": v["first_contact"].isoformat(),
                "iklass": v["iklass"],
                "abdul": v["abdul"],
            }
            for k, v in contacted_employers.items()
        }
        text = f"{STORAGE_TAG}\n{json.dumps(raw)}"
        if storage_msg_id:
            await client.edit_message("me", storage_msg_id, text)
        else:
            msg = await client.send_message("me", text)
            storage_msg_id = msg.id
    except Exception as e:
        logger.error(f"Failed to save contacted employers: {e}")


def get_employer_status(poster_id: int) -> dict:
    """Returns what actions are still allowed for this employer."""
    if poster_id not in contacted_employers:
        return {"iklass": True, "abdul": True, "days_since": 0}
    record = contacted_employers[poster_id]
    days_since = (datetime.now() - record["first_contact"]).days
    if days_since >= COOLDOWN_DAYS:
        # Cooldown expired — reset and allow both
        return {"iklass": True, "abdul": True, "days_since": days_since}
    return {
        "iklass": not record["iklass"],   # True = still needs to send
        "abdul": not record["abdul"],
        "days_since": days_since,
    }


def has_skill_keyword(text: str) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in SKILL_KEYWORDS)


async def is_employer_post_ai(text: str) -> bool:
    if not ai_client:
        logger.error("ANTHROPIC_API_KEY not set — cannot classify, skipping")
        return False
    try:
        response = ai_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": (
                    "Read this Telegram group message carefully.\n\n"
                    f"Message: {text[:600]}\n\n"
                    "Is the person who wrote this an EMPLOYER offering a job/role to others, "
                    "or a JOB SEEKER advertising themselves and looking for work?\n\n"
                    "Reply with exactly one word: EMPLOYER or SEEKER"
                )
            }]
        )
        result = response.content[0].text.strip().upper()
        logger.info(f"AI classification: {result} | Message: {text[:80]}")
        return "EMPLOYER" in result
    except Exception as e:
        logger.error(f"AI classification error: {e} — skipping to avoid false positive")
        return False


def log_sent_application(poster_id, account, message_text, status):
    path = "sent_applications.json"
    apps = json.load(open(path)) if os.path.exists(path) else []
    apps.append({
        "app_id": len(apps) + 1,
        "poster_id": poster_id,
        "account": account,
        "message_sent": message_text[:100],
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
    })
    json.dump(apps, open(path, "w"), indent=2)


async def notify_owner(client, text):
    if not NOTIFY_CHAT_ID:
        return
    try:
        await client.send_message(NOTIFY_CHAT_ID, text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def send_messages(iklass_client, abdul_client, poster_id, poster_name, notify):
    status = get_employer_status(poster_id)

    if not status["iklass"] and not status["abdul"]:
        msg = f"Skipped {poster_name} — both accounts already messaged {status['days_since']} day(s) ago. Cooldown: {COOLDOWN_DAYS} days."
        logger.info(msg)
        await notify(f"Job Hunter: {msg}")
        return

    # Initialise or reset record before any async delay
    if poster_id not in contacted_employers or status["days_since"] >= COOLDOWN_DAYS:
        contacted_employers[poster_id] = {"first_contact": datetime.now(), "iklass": False, "abdul": False}

    iklass_message = random.choice(IKLASS_VARIANTS)
    abdul_message = random.choice(ABDUL_VARIANTS)

    if status["iklass"]:
        try:
            await iklass_client.send_message(poster_id, iklass_message)
            contacted_employers[poster_id]["iklass"] = True
            await save_contacted(iklass_client)
            log_sent_application(poster_id, "Iklass", iklass_message, "success")
            logger.info(f"Iklass sent to {poster_name} ({poster_id})")
        except Exception as e:
            logger.error(f"Iklass failed to send to {poster_name}: {e}")
            await notify(f"Job Hunter: Iklass failed to message {poster_name}\n{e}")
    else:
        logger.info(f"Iklass already messaged {poster_name}, skipping Iklass")

    if status["abdul"]:
        delay = random.randint(180, 420)
        logger.info(f"Waiting {delay}s before Abdul sends...")
        await asyncio.sleep(delay)
        try:
            await abdul_client.send_message(poster_id, abdul_message)
            contacted_employers[poster_id]["abdul"] = True
            await save_contacted(iklass_client)
            log_sent_application(poster_id, "Abdul", abdul_message, "success")
            logger.info(f"Abdul sent to {poster_name} ({poster_id})")
        except Exception as e:
            logger.error(f"Abdul failed to send to {poster_name}: {e}")
            await notify(f"Job Hunter: Abdul failed to message {poster_name}\n{e}")
    else:
        logger.info(f"Abdul already messaged {poster_name}, skipping Abdul")

    iklass_done = contacted_employers[poster_id]["iklass"]
    abdul_done = contacted_employers[poster_id]["abdul"]
    await notify(
        f"Job Hunter Update — {poster_name}\n"
        f"Iklass: {'sent' if iklass_done else 'failed'}\n"
        f"Abdul: {'sent' if abdul_done else 'failed'}"
    )


async def main():
    iklass_client = TelegramClient(StringSession(IKLASS_SESSION), API_ID, API_HASH)
    abdul_client = TelegramClient(StringSession(ABDUL_SESSION), API_ID, API_HASH)

    await iklass_client.start()
    await abdul_client.start()

    await load_contacted(iklass_client)

    async def notify(text):
        await notify_owner(iklass_client, text)

    @iklass_client.on(events.NewMessage(chats=TARGET_GROUPS))
    async def handle_message(event):
        message_text = event.message.text or ""
        if not message_text:
            return

        # Step 1: cheap keyword pre-filter
        if not has_skill_keyword(message_text):
            return

        # Step 2: AI classifies employer vs job seeker
        if not await is_employer_post_ai(message_text):
            logger.info("Skipped — classified as job seeker")
            return

        sender = await event.get_sender()
        poster_id = event.sender_id
        poster_name = getattr(sender, "first_name", None) or "Unknown"
        chat = await event.get_chat()
        group_name = getattr(chat, "title", "Unknown Group")

        logger.info(f"MATCH: {poster_name} in {group_name}")
        await notify(
            f"Job Hunter Match\n\n"
            f"Group: {group_name}\n"
            f"Poster: {poster_name} (ID: {poster_id})\n\n"
            f"{message_text[:300]}"
        )
        await send_messages(iklass_client, abdul_client, poster_id, poster_name, notify)

    logger.info("Job Hunter Bot started — listening for employer posts...")
    await notify("Job Hunter is online and listening.")
    await iklass_client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
