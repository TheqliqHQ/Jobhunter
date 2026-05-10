import json
import os
import random
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot tokens
IKLASS_TOKEN = os.getenv("IKLASS_TOKEN")
ABDUL_TOKEN = os.getenv("ABDUL_TOKEN")

# Group IDs (get these after bot joins groups)
TARGET_GROUPS = {
    "PrimeClubOFM": -1001234567890,  # Replace with actual group ID
    "ofmjobs": -1001234567890,       # Replace with actual group ID
    "ofmpros": -1001234567890,       # Replace with actual group ID
}

# Keywords for filtering
EMPLOYER_KEYWORDS = [
    "HIRING",
    "we are seeking",
    "we're looking",
    "recruitment",
    "job opening",
    "position available",
    "requirements:",
    "responsibilities:",
    "details:",
    "location:",
    "payment:",
    "salary:",
    "compensation:",
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

# Message variants for Iklass
IKLASS_VARIANTS = [
    """Hey! Just saw your post about the AI content operator role. I've got 2 years doing 
similar work with Kling and other tools. Keen to apply if you're still hiring.

Cheers,
Iklass""",
    
    """Hi! Interested in the AI content role. I've got solid 2 years experience with 
Kling AI and video editing. Would love to chat about this opportunity.

Talk soon,
Iklass""",
    
    """Just came across your hiring post. I've been creating AI content for 2 years now, 
pretty familiar with Kling and similar tools. Let's see if we're a good fit!

Iklass"""
]

# Message variants for Abdul
ABDUL_VARIANTS = [
    """Hey! Saw your posting for the content creator role. Been in the AI content space 
for 2 years, comfortable with Kling and video editing. Interested!

Cheers,
Abdul""",
    
    """Hi there! Your AI content role caught my attention. 2 years experience with video 
creation and AI tools. Would be great to discuss further.

Best,
Abdul""",
    
    """Just found your job post. I'm a content creator with 2 years in the AI space, 
familiar with Kling and the whole workflow. Let's connect!

Abdul"""
]

# Track last match time for rate limiting (10 mins between matches)
last_match_time = 0
last_sent_to = set()  # Track who we've already sent to


def is_employer_post(message_text):
    """Check if message is from employer (contains hiring keywords)"""
    text_lower = message_text.lower()
    return any(keyword.lower() in text_lower for keyword in EMPLOYER_KEYWORDS)


def has_skill_match(message_text):
    """Check if message contains skill keywords"""
    text_lower = message_text.lower()
    return any(skill.lower() in text_lower for skill in SKILL_KEYWORDS)


def log_matched_job(poster_id, job_text, group_name):
    """Log matched job to JSON"""
    if not os.path.exists("matched_jobs.json"):
        matched_jobs = []
    else:
        with open("matched_jobs.json", "r") as f:
            matched_jobs = json.load(f)
    
    matched_jobs.append({
        "job_id": len(matched_jobs) + 1,
        "poster_id": poster_id,
        "job_text": job_text[:200],  # Store first 200 chars
        "group": group_name,
        "matched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open("matched_jobs.json", "w") as f:
        json.dump(matched_jobs, f, indent=2)


def log_sent_application(poster_id, account, message_text, status):
    """Log sent application to JSON"""
    if not os.path.exists("sent_applications.json"):
        sent_apps = []
    else:
        with open("sent_applications.json", "r") as f:
            sent_apps = json.load(f)
    
    sent_apps.append({
        "app_id": len(sent_apps) + 1,
        "poster_id": poster_id,
        "account": account,
        "message_sent": message_text[:100],  # Store first 100 chars
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status
    })
    
    with open("sent_applications.json", "w") as f:
        json.dump(sent_apps, f, indent=2)


async def send_messages(update: Update, context: ContextTypes.DEFAULT_TYPE, poster_id: int, poster_name: str):
    """Send messages from both accounts with 3-7 min delay"""
    global last_sent_to
    
    if poster_id in last_sent_to:
        logger.info(f"Already sent to {poster_id}, skipping")
        return
    
    # Get applications for both accounts
    iklass_message = random.choice(IKLASS_VARIANTS)
    abdul_message = random.choice(ABDUL_VARIANTS)
    
    try:
        # Send from Iklass (first)
        iklass_app = Application.builder().token(IKLASS_TOKEN).build()
        await iklass_app.bot.send_message(
            chat_id=poster_id,
            text=iklass_message
        )
        log_sent_application(poster_id, "Iklass", iklass_message, "success")
        logger.info(f"✅ Iklass sent to {poster_name} ({poster_id})")
        
        # Random delay 3-7 minutes
        delay = random.randint(180, 420)  # 3-7 mins in seconds
        logger.info(f"⏳ Waiting {delay}s before Abdul sends...")
        await asyncio.sleep(delay)
        
        # Send from Abdul (second)
        abdul_app = Application.builder().token(ABDUL_TOKEN).build()
        await abdul_app.bot.send_message(
            chat_id=poster_id,
            text=abdul_message
        )
        log_sent_application(poster_id, "Abdul", abdul_message, "success")
        logger.info(f"✅ Abdul sent to {poster_name} ({poster_id})")
        
        last_sent_to.add(poster_id)
        
    except Exception as e:
        logger.error(f"❌ Error sending message to {poster_id}: {str(e)}")
        log_sent_application(poster_id, "Both", "Failed", "failed")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming group messages"""
    global last_match_time
    
    # Only process group messages
    if update.message.chat.type not in ["group", "supergroup"]:
        return
    
    message_text = update.message.text or ""
    poster_id = update.message.from_user.id
    poster_name = update.message.from_user.first_name or "Unknown"
    group_name = update.message.chat.title
    
    # Rate limiting: 10 mins between matches
    current_time = datetime.now().timestamp()
    if current_time - last_match_time < 600:  # 600 seconds = 10 mins
        return
    
    # Check if employer post
    if not is_employer_post(message_text):
        logger.info(f"⊘ Not an employer post in {group_name}")
        return
    
    # Check if has skill match
    if not has_skill_match(message_text):
        logger.info(f"⊘ No skill match in {group_name}")
        return
    
    # Match found!
    logger.info(f"🎯 MATCH FOUND in {group_name}!")
    logger.info(f"   Poster: {poster_name} (ID: {poster_id})")
    logger.info(f"   Text: {message_text[:100]}...")
    
    # Log the matched job
    log_matched_job(poster_id, message_text, group_name)
    
    # Send messages
    last_match_time = current_time
    await send_messages(update, context, poster_id, poster_name)


async def main():
    """Start both bot applications"""
    
    # Iklass bot
    iklass_app = Application.builder().token(IKLASS_TOKEN).build()
    iklass_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Abdul bot
    abdul_app = Application.builder().token(ABDUL_TOKEN).build()
    abdul_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Job Hunter Bot starting...")
    logger.info(f"📍 Monitoring groups: {list(TARGET_GROUPS.keys())}")
    logger.info(f"🎯 Watching for: {', '.join(SKILL_KEYWORDS[:5])}...")
    
    async with iklass_app:
        async with abdul_app:
            await iklass_app.start()
            await abdul_app.start()
            logger.info("✅ Both bots are running!")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                await iklass_app.stop()
                await abdul_app.stop()


if __name__ == "__main__":
    asyncio.run(main())
