import asyncio
import json
import logging
import os
import random
from datetime import datetime

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
ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TARGET_GROUPS = [
    -1001854701169,  # PrimeClubOFM
    -1001891392293,  # ofmjobs
    -1002501290895,  # ofmpros
]

JOB_SEEKER_KEYWORDS = [
    "looking for work",
    "looking for a job",
    "looking for job",
    "seeking work",
    "seeking a job",
    "seeking employment",
    "open to work",
    "open to opportunities",
    "available for",
    "available to work",
    "i am a",
    "i'm a",
    "hire me",
    "portfolio",
    "my work",
    "my experience",
    "years of experience",
    "please dm me",
    "please contact me",
    "reach out to me",
    "i can do",
    "i do ",
    "i offer",
    "my services",
]

EMPLOYER_KEYWORDS = [
    "hiring", "we need", "we are looking", "we are seeking",
    "we're looking", "we're seeking", "looking for", "seeking a",
    "need a", "need an", "recruitment", "job opening", "position available",
    "open position", "requirements:", "responsibilities:", "details:",
    "location:", "payment:", "salary:", "compensation:",
    "dm me", "dm us", "apply now", "send your",
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

COOLDOWN_DAYS = 7
last_match_time = 0
contacted_employers = {}  # poster_id -> last messaged datetime


def load_contacted_employers():
    global contacted_employers
    if os.path.exists("contacted_employers.json"):
        raw = json.load(open("contacted_employers.json"))
        contacted_employers = {int(k): datetime.fromisoformat(v) for k, v in raw.items()}


def save_contacted_employers():
    raw = {str(k): v.isoformat() for k, v in contacted_employers.items()}
    json.dump(raw, open("contacted_employers.json", "w"), indent=2)


def can_message_employer(poster_id):
    if poster_id not in contacted_employers:
        return True
    days_since = (datetime.now() - contacted_employers[poster_id]).days
    return days_since >= COOLDOWN_DAYS


def has_skill_keyword(text):
    lower = text.lower()
    return any(k.lower() in lower for k in SKILL_KEYWORDS)


def is_employer_post(text):
    lower = text.lower()
    return any(k.lower() in lower for k in EMPLOYER_KEYWORDS)


async def is_employer_post_ai(text):
    """Use Claude to confirm this is an employer posting a vacancy, not a job seeker."""
    try:
        response = ai_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": (
                    "Is this Telegram message from an EMPLOYER posting a job vacancy, "
                    "or from a JOB SEEKER looking for work?\n\n"
                    f"Message: {text[:500]}\n\n"
                    "Reply with only one word: EMPLOYER or SEEKER"
                )
            }]
        )
        result = response.content[0].text.strip().upper()
        logger.info(f"AI classification: {result}")
        return result == "EMPLOYER"
    except Exception as e:
        logger.error(f"AI classification failed: {e}")
        return is_employer_post(text)


def has_skill_match(text):
    lower = text.lower()
    return any(k.lower() in lower for k in SKILL_KEYWORDS)


def log_matched_job(poster_id, job_text, group_name):
    path = "matched_jobs.json"
    jobs = json.load(open(path)) if os.path.exists(path) else []
    jobs.append({
        "job_id": len(jobs) + 1,
        "poster_id": poster_id,
        "job_text": job_text[:200],
        "group": group_name,
        "matched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    json.dump(jobs, open(path, "w"), indent=2)


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


async def notify_owner(iklass_client, text):
    if not NOTIFY_CHAT_ID:
        return
    try:
        await iklass_client.send_message(NOTIFY_CHAT_ID, text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def send_messages(iklass_client, abdul_client, poster_id, poster_name, notify):
    global contacted_employers

    if not can_message_employer(poster_id):
        days_since = (datetime.now() - contacted_employers[poster_id]).days
        msg = f"Skipped {poster_name} — messaged {days_since} day(s) ago (cooldown: {COOLDOWN_DAYS} days)"
        logger.info(msg)
        await notify(f"Job Hunter: {msg}")
        return

    iklass_message = random.choice(IKLASS_VARIANTS)
    abdul_message = random.choice(ABDUL_VARIANTS)

    try:
        await iklass_client.send_message(poster_id, iklass_message)
        log_sent_application(poster_id, "Iklass", iklass_message, "success")
        logger.info(f"Iklass sent to {poster_name} ({poster_id})")

        delay = random.randint(180, 420)
        logger.info(f"Waiting {delay}s before Abdul sends...")
        await asyncio.sleep(delay)

        await abdul_client.send_message(poster_id, abdul_message)
        log_sent_application(poster_id, "Abdul", abdul_message, "success")
        logger.info(f"Abdul sent to {poster_name} ({poster_id})")

        contacted_employers[poster_id] = datetime.now()
        save_contacted_employers()

    except Exception as e:
        msg = f"Error sending to {poster_name} ({poster_id}): {e}"
        logger.error(msg)
        log_sent_application(poster_id, "Both", "Failed", "failed")
        await notify(f"Job Hunter Error\n\n{msg}")


async def main():
    global last_match_time

    iklass_client = TelegramClient(StringSession(IKLASS_SESSION), API_ID, API_HASH)
    abdul_client = TelegramClient(StringSession(ABDUL_SESSION), API_ID, API_HASH)

    load_contacted_employers()

    await iklass_client.start()
    await abdul_client.start()

    logger.info("Job Hunter Bot starting...")
    logger.info(f"Monitoring {len(TARGET_GROUPS)} groups")


    async def notify(text):
        await notify_owner(iklass_client, text)

    @iklass_client.on(events.NewMessage(chats=TARGET_GROUPS))
    async def handle_message(event):
        global last_match_time

        message_text = event.message.text or ""
        poster_id = event.sender_id
        sender = await event.get_sender()
        poster_name = getattr(sender, "first_name", None) or "Unknown"
        chat = await event.get_chat()
        group_name = getattr(chat, "title", "Unknown Group")

        current_time = datetime.now().timestamp()
        cooldown_remaining = 600 - (current_time - last_match_time)
        if cooldown_remaining > 0:
            logger.info(f"Rate limit active, {int(cooldown_remaining)}s remaining")
            await notify(f"Job Hunter: Skipped post in {group_name} — rate limit active ({int(cooldown_remaining)}s left)\n\nPost: {message_text[:100]}")
            return

        if not has_skill_keyword(message_text):
            return

        if not await is_employer_post_ai(message_text):
            logger.info("Skipping — AI classified as job seeker post")
            return

        logger.info(f"MATCH FOUND in {group_name}! Poster: {poster_name} ({poster_id})")
        await notify(f"Job Hunter: Match found in {group_name}!\n\nPoster: {poster_name}\n\nPost: {message_text[:200]}")
        log_matched_job(poster_id, message_text, group_name)
        last_match_time = current_time
        await send_messages(iklass_client, abdul_client, poster_id, poster_name, notify)

    await notify(f"Job Hunter is online and listening!")
    logger.info("Listening for job posts...")

    @iklass_client.on(events.NewMessage)
    async def debug_all(event):
        try:
            chat = await event.get_chat()
            chat_id = getattr(chat, "id", None)
            chat_title = getattr(chat, "title", "Private/Unknown")
            text = (event.message.text or "")[:80]
            logger.info(f"MSG in [{chat_id}] {chat_title}: {text}")
            await notify(f"DEBUG — Message in [{chat_id}] {chat_title}:\n{text}")
        except Exception as e:
            logger.error(f"Debug handler error: {e}")

    await iklass_client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
