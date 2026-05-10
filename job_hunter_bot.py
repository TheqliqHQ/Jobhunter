import json
import os
import random
import asyncio
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IKLASS_TOKEN = os.getenv("IKLASS_TOKEN")
ABDUL_TOKEN = os.getenv("ABDUL_TOKEN")
NOTIFY_CHAT_ID = os.getenv("NOTIFY_CHAT_ID")  # Your personal Telegram chat ID

TARGET_GROUPS = {
    "PrimeClubOFM": -1001854701169,
    "ofmjobs": -1001891392293,
    "ofmpros": -1002501290895,
}

EMPLOYER_KEYWORDS = [
    "HIRING",
    "we need",
    "we are looking",
    "we are seeking",
    "we're looking",
    "we're seeking",
    "looking for",
    "seeking a",
    "need a",
    "need an",
    "recruitment",
    "job opening",
    "position available",
    "open position",
    "requirements:",
    "responsibilities:",
    "details:",
    "location:",
    "payment:",
    "salary:",
    "compensation:",
    "dm me",
    "dm us",
    "apply now",
    "send your",
]

SKILL_KEYWORDS = [
    "AI content",
    "AI model",
    "Kling AI",
    "Kling",
    "CapCut",
    "Nano Banana",
    "Freepik",
    "Wavespeed",
    "Higgsfield",
    "Comfy UI",
    "content creator",
    "content operator",
    "video editing",
    "visual storytelling",
    "AI tools",
    "creative",
]

IKLASS_VARIANTS = [
    """Hey! Just saw your post about the AI content operator role. I've got 2 years doing \
similar work with Kling and other tools. Keen to apply if you're still hiring.

Cheers,
Iklass""",
    """Hi! Interested in the AI content role. I've got solid 2 years experience with \
Kling AI and video editing. Would love to chat about this opportunity.

Talk soon,
Iklass""",
    """Just came across your hiring post. I've been creating AI content for 2 years now, \
pretty familiar with Kling and similar tools. Let's see if we're a good fit!

Iklass""",
]

ABDUL_VARIANTS = [
    """Hey! Saw your posting for the content creator role. Been in the AI content space \
for 2 years, comfortable with Kling and video editing. Interested!

Cheers,
Abdul""",
    """Hi there! Your AI content role caught my attention. 2 years experience with video \
creation and AI tools. Would be great to discuss further.

Best,
Abdul""",
    """Just found your job post. I'm a content creator with 2 years in the AI space, \
familiar with Kling and the whole workflow. Let's connect!

Abdul""",
]

last_match_time = 0
last_sent_to = set()


def is_employer_post(text):
    lower = text.lower()
    return any(k.lower() in lower for k in EMPLOYER_KEYWORDS)


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


async def notify_owner(text):
    if not NOTIFY_CHAT_ID:
        return
    try:
        async with Bot(IKLASS_TOKEN) as bot:
            await bot.send_message(chat_id=NOTIFY_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Failed to send owner notification: {e}")


async def try_send(bot: Bot, chat_id, username, message):
    """Try sending by user ID first, fall back to @username if privacy blocks it."""
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        if ("Forbidden" in str(e) or "blocked" in str(e).lower()) and username:
            try:
                await bot.send_message(chat_id=f"@{username}", text=message)
                return True
            except Exception:
                pass
        raise


async def send_messages(poster_id, poster_name, poster_username):
    global last_sent_to

    if poster_id in last_sent_to:
        logger.info(f"Already sent to {poster_id}, skipping")
        return

    iklass_message = random.choice(IKLASS_VARIANTS)
    abdul_message = random.choice(ABDUL_VARIANTS)

    try:
        async with Bot(IKLASS_TOKEN) as iklass_bot:
            await try_send(iklass_bot, poster_id, poster_username, iklass_message)
        log_sent_application(poster_id, "Iklass", iklass_message, "success")
        logger.info(f"Iklass sent to {poster_name} ({poster_id})")

        delay = random.randint(180, 420)
        logger.info(f"Waiting {delay}s before Abdul sends...")
        await asyncio.sleep(delay)

        async with Bot(ABDUL_TOKEN) as abdul_bot:
            await try_send(abdul_bot, poster_id, poster_username, abdul_message)
        log_sent_application(poster_id, "Abdul", abdul_message, "success")
        logger.info(f"Abdul sent to {poster_name} ({poster_id})")

        last_sent_to.add(poster_id)

    except Exception as e:
        if "Forbidden" in str(e) or "blocked" in str(e).lower():
            msg = (
                f"Privacy block — could not DM {poster_name}"
                + (f" (@{poster_username})" if poster_username else f" (ID: {poster_id})")
                + "\nThey have DMs restricted. You may need to reach out manually."
            )
            logger.warning(msg)
            log_sent_application(poster_id, "Both", "Blocked by privacy settings", "blocked")
            await notify_owner(f"Job Hunter Alert\n\n{msg}")
        else:
            msg = f"Error sending to {poster_name} ({poster_id}): {e}"
            logger.error(msg)
            log_sent_application(poster_id, "Both", "Failed", "failed")
            await notify_owner(f"Job Hunter Error\n\n{msg}")


async def handle_message(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    global last_match_time

    if not update.message or update.message.chat.type not in ["group", "supergroup"]:
        return

    message_text = update.message.text or ""
    poster_id = update.message.from_user.id
    poster_name = update.message.from_user.first_name or "Unknown"
    poster_username = update.message.from_user.username  # None if they have no @username
    group_name = update.message.chat.title

    current_time = datetime.now().timestamp()
    if current_time - last_match_time < 600:
        return

    if not is_employer_post(message_text):
        return

    if not has_skill_match(message_text):
        return

    logger.info(f"MATCH FOUND in {group_name}! Poster: {poster_name} ({poster_id})")
    log_matched_job(poster_id, message_text, group_name)
    last_match_time = current_time
    await send_messages(poster_id, poster_name, poster_username)


def main():
    logger.info("Job Hunter Bot starting...")
    logger.info(f"Monitoring: {list(TARGET_GROUPS.keys())}")

    app = Application.builder().token(IKLASS_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running!")
    app.run_polling()


if __name__ == "__main__":
    main()
