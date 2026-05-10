# 🚀 Railway Deployment Guide - Job Hunter Bot

## Overview
This guide will help you deploy your dual-account job hunter bot to Railway for 24/7 uptime.

---

## Step 1: Prepare for Deployment

### 1.1 Create a GitHub Repository
```bash
# Create a new folder for your project
mkdir job-hunter-bot
cd job-hunter-bot

# Initialize git
git init

# Create these files in the folder:
# - job_hunter_bot.py (main bot code)
# - requirements.txt (dependencies)
# - .env (bot tokens - optional, we'll use Railway secrets instead)
# - Procfile (tells Railway how to run the bot)
```

### 1.2 Create a Procfile
Create a file named `Procfile` (no extension) with this content:
```
worker: python job_hunter_bot.py
```

### 1.3 Push to GitHub
```bash
# Add all files
git add .

# Commit
git commit -m "Initial job hunter bot setup"

# Create repo on GitHub: https://github.com/new
# Then push (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/job-hunter-bot.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Account

1. Go to **https://railway.app**
2. Click **Sign Up** (use GitHub to login - easier)
3. Authorize Railway to access your GitHub

---

## Step 3: Deploy Bot to Railway

### 3.1 Create New Project
1. Click **New Project**
2. Select **Deploy from GitHub**
3. Choose your `job-hunter-bot` repository
4. Click **Deploy**

### 3.2 Add Environment Variables
1. In Railway dashboard, find your project
2. Click on the **bot service**
3. Go to **Variables** tab
4. Add these variables:
   ```
   IKLASS_TOKEN=8527170720:AAF9LYagaYhg7SCAPCF6GIgdooBzC4CTDHo
   ABDUL_TOKEN=8685949744:AAFPF3S3XRyte42IZEzy0CCPNAxZVwCLH3o
   ```
5. Click **Save**

### 3.3 Check Deployment
1. Go to **Deployments** tab
2. Wait for status to show ✅ **Success**
3. Check **Logs** to see bot running

---

## Step 4: Add Bots to Telegram Groups

### Important: Get Group IDs First

Before the bot can work, you need the **Group IDs** for:
- PrimeClubOFM
- ofmjobs
- ofmpros

**How to get Group IDs:**

**Method 1 (Easiest):**
1. Add bot to the group
2. In the group, send a message
3. The bot will log the group ID in Railway logs
4. Copy it from logs

**Method 2 (Manual):**
1. In Telegram, go to group
2. Click group name
3. Get the Group ID (starts with `-100`)

### Add Bot to Groups

1. Go to **PrimeClubOFM** group
2. Click group name → **Add Member**
3. Search for `@[YOUR_IKLASS_BOT_USERNAME]` (created at @BotFather)
4. Add the bot
5. Repeat for Abdul bot
6. Repeat for all 3 groups

---

## Step 5: Update Bot Code with Group IDs

Once you have the group IDs, update the bot code:

1. In your GitHub repo, edit `job_hunter_bot.py`
2. Find this section:
```python
TARGET_GROUPS = {
    "PrimeClubOFM": -1001234567890,  # Replace with actual group ID
    "ofmjobs": -1001234567890,       # Replace with actual group ID
    "ofmpros": -1001234567890,       # Replace with actual group ID
}
```

3. Replace with real IDs (from Step 4)
4. Commit and push:
```bash
git add job_hunter_bot.py
git commit -m "Add group IDs"
git push
```

5. Railway will auto-deploy the update ✅

---

## Step 6: Monitor the Bot

### Check Logs in Railway
1. Open your project in Railway
2. Click **Logs** tab
3. You'll see:
   ```
   🤖 Job Hunter Bot starting...
   📍 Monitoring groups: ['PrimeClubOFM', 'ofmjobs', 'ofmpros']
   ✅ Both bots are running!
   ```

### Check JSON Files
The bot creates 2 JSON files in Railway's file system:
- `matched_jobs.json` - All jobs the bot found
- `sent_applications.json` - All messages sent

You can download these from Railway **File** tab

---

## Step 7: Troubleshooting

### Bot Not Responding
```
❌ Check:
1. Bot tokens are correct (copy from @BotFather)
2. Bots are added to groups
3. Group IDs are correct in code
4. Railway logs show "✅ Both bots are running!"
```

### Messages Not Sending
```
❌ Check:
1. Job poster has DMs enabled
2. Bot has permission to send messages
3. No Telegram rate limiting (wait 30 mins)
4. Check Railway logs for errors
```

### Rate Limiting
```
ℹ️ If you get "Too Many Requests":
- Railway will auto-retry
- Check back in 1 hour
- Telegram limits ~30 messages/second globally
```

---

## Step 8: Customize Settings

Want to adjust the bot? Edit `job_hunter_bot.py`:

### Change Message Delay
Find this line:
```python
delay = random.randint(180, 420)  # 3-7 mins in seconds
```
Change to your preference:
- `180, 240` = 3-4 mins
- `300, 600` = 5-10 mins

### Change Rate Limiting
Find this line:
```python
if current_time - last_match_time < 600:  # 600 seconds = 10 mins
```
Change to your preference:
- `300` = 5 mins between matches
- `900` = 15 mins between matches

### Add More Keywords
Find this section:
```python
SKILL_KEYWORDS = [
    "AI content",
    "Kling",
    # Add more here...
]
```

After each change, commit and push to GitHub → Railway auto-deploys!

---

## Step 9: Keep Bot Running 24/7

Railway keeps your bot running automatically. But:

✅ **Do this:**
- Keep your GitHub repo public (Railway needs access)
- Check Railway dashboard weekly
- Monitor bot logs for errors

❌ **Don't:**
- Delete the Procfile
- Change bot tokens without updating Railway vars
- Disable the Railway project

---

## Cost on Railway

**Good news:** Railway offers:
- **$5/month free credit** (enough for this bot)
- Bots typically use **$2-3/month**
- You get **first $5 free**, then $0.50/hour for extra

**Your bot cost:** ~$2/month (very cheap!)

---

## Support

If something breaks:

1. **Check Railway logs** - Usually tells you the error
2. **Check bot tokens** - Most common issue
3. **Check group IDs** - Second most common
4. **Restart bot** - In Railway dashboard, click **Restart**

---

## Next Steps

✅ You now have a 24/7 job hunter bot!

**Optional improvements:**
- Add admin commands (/stats, /pause, /resume)
- Email notifications when jobs matched
- Weekly summary report
- Dashboard to view matched jobs

**Ready?** Push your code to GitHub and Railway will auto-deploy! 🚀

