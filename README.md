# 🤖 Dual-Account Job Hunter Bot

A sophisticated Telegram bot that automatically hunts for AI content creation jobs across multiple groups and applies on your behalf using 2 different accounts with randomized messages.

---

## ⚡ Features

✅ **Dual Account System**
- Messages from both Iklass & Abdul accounts
- Randomized message variants (looks natural, not bot-like)
- 3-7 minute delays between sends

✅ **Smart Job Detection**
- Employer post filtering (avoids applicants)
- AI/content keyword matching
- 10-minute rate limiting (no spam)

✅ **Persistent Tracking**
- JSON file storage (no database needed)
- Tracks all matched jobs
- Logs all sent applications

✅ **24/7 Uptime**
- Deployed on Railway (always running)
- Auto-restarts if it crashes
- Nigeria-friendly (works great here!)

---

## 📊 How It Works

```
Job Posted in Telegram Group
    ↓
Bot detects employer post + skill keywords
    ↓
Matches your criteria? YES
    ↓
Log job to matched_jobs.json
    ↓
Iklass bot sends random variant message
    ↓
Wait 3-7 mins (random)
    ↓
Abdul bot sends different random variant
    ↓
Log to sent_applications.json
    ↓
Wait 10 mins before next match
    ↓
Repeat! ✅
```

---

## 🎯 What Gets Matched

**Job Posts MUST have:**
- ✅ "HIRING" OR "we are seeking" OR similar employer keywords
- ✅ "Kling AI" OR "CapCut" OR "content creator" OR similar skill keywords

**Won't send to:**
- ❌ Applicant posts (people looking for jobs)
- ❌ Non-employer messages
- ❌ Same person twice (tracks by user ID)

---

## 📁 Files Included

```
job-hunter-bot/
├── job_hunter_bot.py          # Main bot code (ready to run)
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway configuration
├── .env                        # Bot tokens (keep secret!)
├── QUICK_START.md             # Fast setup guide (READ THIS FIRST!)
├── RAILWAY_DEPLOYMENT.md      # Detailed Railway guide
└── README.md                  # This file
```

---

## 🚀 Quick Start (5 mins)

### 1. Get Bot Usernames
```
Open Telegram → Search @BotFather
/mybots → Select Iklass bot → Check username (e.g., @IklassJobBot)
Repeat for Abdul bot
```

### 2. Add Bots to Groups
```
In each group (PrimeClubOFM, ofmjobs, ofmpros):
  Click group name → Add Member
  Search for bot username → Add
Repeat for both bots
```

### 3. Get Group IDs
```
Send a test message in group
Visit: https://api.telegram.org/botYOUR_TOKEN/getUpdates
Find "chat":{"id": (copy this number)
Note down all 3 group IDs
```

### 4. Update Bot Code
```
Edit job_hunter_bot.py
Find TARGET_GROUPS section
Replace with your real group IDs
Save
```

### 5. Deploy to Railway
```
1. Create GitHub account (free)
2. Create repo, upload 3 files (job_hunter_bot.py, requirements.txt, Procfile)
3. Go to railway.app, sign up with GitHub
4. Click "Deploy from GitHub" → Select your repo
5. Add IKLASS_TOKEN & ABDUL_TOKEN in Variables
6. Done! Bot runs 24/7
```

**See QUICK_START.md for detailed steps!**

---

## 🔧 Configuration

### Adjust Message Delay
In `job_hunter_bot.py`, find:
```python
delay = random.randint(180, 420)  # 3-7 mins
```

Change to:
- `random.randint(180, 240)` = 3-4 mins
- `random.randint(300, 600)` = 5-10 mins

### Change Rate Limiting (10 mins)
Find:
```python
if current_time - last_match_time < 600:  # 600 = 10 mins
```

Change `600` to:
- `300` = 5 mins between matches
- `900` = 15 mins between matches

### Add More Keywords
Find `SKILL_KEYWORDS` list and add:
```python
SKILL_KEYWORDS = [
    "Kling AI",
    "CapCut",
    "your new keyword here",  # Add like this
    # ...
]
```

### Customize Messages
Find `IKLASS_VARIANTS` and `ABDUL_VARIANTS` lists. Edit any message you want.

---

## 📊 Monitoring

### Check Bot Status
1. Go to **railway.app** → Your project
2. Click **Logs** tab
3. See real-time bot activity

### View Matched Jobs
Files created automatically:
- `matched_jobs.json` - All jobs detected
- `sent_applications.json` - All messages sent

Download from Railway **Files** tab to view locally.

### Example Log Output
```
🤖 Job Hunter Bot starting...
📍 Monitoring groups: ['PrimeClubOFM', 'ofmjobs', 'ofmpros']
✅ Both bots are running!
🎯 MATCH FOUND in PrimeClubOFM!
   Poster: John Doe (ID: 123456789)
   Text: HIRING: Kling AI Content Operator...
✅ Iklass sent to John Doe (123456789)
⏳ Waiting 245s before Abdul sends...
✅ Abdul sent to John Doe (123456789)
```

---

## ⚠️ Important Notes

### Telegram Rate Limits
- Telegram allows ~30 messages/second globally
- Our 10-min rate limiting is safe
- If you hit limits, Railway will auto-retry

### Privacy & Terms
- Make sure sending unsolicited DMs is allowed in your groups
- Recruiters should welcome job inquiries
- Messages look natural (not obviously automated)

### Bot Tokens Security
- **NEVER share** your bot tokens
- Keep `.env` file secret
- Use Railway Variables for production (not in code)

---

## 🐛 Troubleshooting

### "Bot is not responding"
```
✓ Check bot is added to groups
✓ Verify group IDs are correct
✓ Check Railway logs for errors
✓ Make sure tokens are right
```

### "Messages not sending to recruiter"
```
✓ Recruiter might have DMs disabled
✓ Check Railway logs for errors
✓ Telegram might be rate-limiting (wait 30 mins)
✓ Recruiter account might be restricted
```

### "Bot tokens invalid"
```
✓ Go to @BotFather, check token again
✓ Copy exactly (no spaces!)
✓ Make sure it's the right bot
✓ Update in Railway Variables
```

### "Group ID not working"
```
✓ Make sure bot is in the group
✓ Use the getUpdates method (detailed in QUICK_START.md)
✓ Group ID starts with -100 or -
✓ Copy exactly, no spaces
```

---

## 💰 Cost

**Railway Pricing:**
- $5/month free credit ✅
- This bot uses ~$2-3/month
- You stay within free tier! ✅

---

## 🎓 What You Learn

Building this bot teaches you:
- Telegram Bot API & python-telegram-bot library
- Async programming in Python
- JSON file handling
- Rate limiting & throttling
- Cloud deployment (Railway)
- Environment variables & secrets management

---

## 📞 Support

**If something breaks:**
1. Check **Railway Logs** (usually shows the error)
2. Check bot **tokens are correct**
3. Check **group IDs are correct**
4. Restart the bot in Railway dashboard

**For detailed help:**
- See **QUICK_START.md** for step-by-step setup
- See **RAILWAY_DEPLOYMENT.md** for advanced config

---

## 🚀 Next Steps

After deployment works:

1. **Monitor for 1 week** - Watch logs, make sure it catches jobs
2. **Optimize keywords** - Add/remove based on what you see
3. **Adjust delays** - Speed up or slow down as needed
4. **Track success** - Save matched_jobs.json, see response rates

---

## 📈 Future Enhancements

Possible improvements:
- ✨ Admin commands (/stats, /pause, /resume via Telegram)
- ✨ Email summaries of matched jobs
- ✨ Weekly report of applications
- ✨ Web dashboard to view jobs
- ✨ Database upgrade (when you scale)

---

## 🎉 You're Ready!

Your bot is:
- ✅ Smart (detects real job posts)
- ✅ Natural (randomized messages)
- ✅ Reliable (runs 24/7)
- ✅ Trackable (logs everything)
- ✅ Cheap ($2-3/month)

**Start the QUICK_START.md guide now!**

Good luck hunting those jobs! 🎯

---

**Made for Opadiran Damilola (Iklass) & Abdul**
Nigerian Job Hunters 🇳🇬
