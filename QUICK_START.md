# 🎯 Quick Start Guide - Job Hunter Bot Setup

## What You Have Now
✅ Bot code ready  
✅ 2 bot tokens (Iklass & Abdul)  
✅ Message variants created  
✅ JSON tracking setup  

---

## Step 1: Get Bot Usernames (2 mins)

### For Iklass Bot:
1. Open Telegram
2. Search: `@BotFather`
3. Send: `/mybots`
4. Select your Iklass bot
5. Click **Edit Bot**
6. Click **Edit Commands** (or find Username in settings)
7. Copy the **username** (e.g., `@IklassJobHunterBot`)
8. Note it down

### For Abdul Bot:
Repeat the same process for Abdul bot
Note: `@AbdulJobHunterBot` (or whatever you named it)

---

## Step 2: Add Bots to Your 3 Telegram Groups (15 mins)

### Add Iklass Bot:

**To PrimeClubOFM group:**
1. Open Telegram → Go to **PrimeClubOFM** group
2. Click group name (top) → **Members** → **Add Member**
3. Search for your Iklass bot username
4. Tap the bot → **Add**
5. ✅ Done

**Repeat for:**
- ofmjobs group
- ofmpros group

**Same process for Abdul bot** (add to all 3 groups)

---

## Step 3: Find Your Group IDs (Important!)

The bot needs to know which groups to listen to. Each group has a unique ID.

### Get Group IDs - Easy Method:

1. Send a test message in **PrimeClubOFM** group
2. Open this URL in browser (with your Iklass token):
```
https://api.telegram.org/bot8527170720:AAF9LYagaYhg7SCAPCF6GIgdooBzC4CTDHo/getUpdates
```

3. Look for `"chat":{"id":` in the page
4. Copy the number (it'll look like: `-1001234567890`)
5. Note it down as **PrimeClubOFM ID**

**Repeat for:**
- ofmjobs group (get its ID)
- ofmpros group (get its ID)

### Alternative Method (Simpler):
Use a bot like `@userinfobot` in the group:
1. Add `@userinfobot` to the group
2. It will show you the group ID immediately
3. Remove the bot after

---

## Step 4: Test the Bot Locally (Optional)

Before deploying to Railway, test on your computer:

### Install Python (if not already):
```bash
python --version
```

### Download the bot files:
1. Create a folder: `job-hunter-bot`
2. Save these 3 files inside:
   - `job_hunter_bot.py` (main code)
   - `requirements.txt` (dependencies)
   - `.env` (with your tokens)

### Install dependencies:
```bash
cd job-hunter-bot
pip install -r requirements.txt
```

### Create `.env` file:
```
IKLASS_TOKEN=8527170720:AAF9LYagaYhg7SCAPCF6GIgdooBzC4CTDHo
ABDUL_TOKEN=8685949744:AAFPF3S3XRyte42IZEzy0CCPNAxZVwCLH3o
```

### Update the code with Group IDs:
In `job_hunter_bot.py`, find:
```python
TARGET_GROUPS = {
    "PrimeClubOFM": -1001234567890,  # Your real ID here
    "ofmjobs": -1001234567890,       # Your real ID here
    "ofmpros": -1001234567890,       # Your real ID here
}
```

Replace `-1001234567890` with your real group IDs

### Run the bot:
```bash
python job_hunter_bot.py
```

You should see:
```
🤖 Job Hunter Bot starting...
📍 Monitoring groups: ['PrimeClubOFM', 'ofmjobs', 'ofmpros']
✅ Both bots are running!
```

**Stop with:** `Ctrl + C`

---

## Step 5: Deploy to Railway (30 mins)

### 5.1 Create GitHub Account
- Go to **https://github.com/signup**
- Sign up (free)

### 5.2 Create GitHub Repository
1. Go to **https://github.com/new**
2. Name it: `job-hunter-bot`
3. Make it **Public**
4. Click **Create Repository**

### 5.3 Upload Files to GitHub
**Option A (Web Upload - Easiest):**
1. In your repo, click **Add File** → **Upload Files**
2. Drag and drop your 3 files:
   - `job_hunter_bot.py`
   - `requirements.txt`
   - `Procfile` (create this with content: `worker: python job_hunter_bot.py`)

**Option B (Using Git - More Advanced):**
```bash
cd job-hunter-bot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/job-hunter-bot.git
git push -u origin main
```

### 5.4 Deploy on Railway
1. Go to **https://railway.app**
2. Sign up with **GitHub**
3. Click **New Project** → **Deploy from GitHub**
4. Select your `job-hunter-bot` repo
5. Click **Deploy**

### 5.5 Add Environment Variables
1. In Railway, click your project
2. Go to **Variables** tab
3. Add:
   ```
   IKLASS_TOKEN=8527170720:AAF9LYagaYhg7SCAPCF6GIgdooBzC4CTDHo
   ABDUL_TOKEN=8685949744:AAFPF3S3XRyte42IZEzy0CCPNAxZVwCLH3o
   ```
4. Click **Save**

### 5.6 Update Bot Code with Group IDs
1. In your GitHub repo, edit `job_hunter_bot.py`
2. Replace the `TARGET_GROUPS` section with your real group IDs
3. Commit and push
4. Railway auto-deploys! ✅

---

## Step 6: Verify Bot is Running

1. Go to Railway dashboard
2. Click **Logs** tab
3. You should see:
   ```
   ✅ Both bots are running!
   📍 Monitoring groups...
   ```

4. Post a test job message in one of your groups with keywords (e.g., "HIRING: Kling AI Content Creator")
5. Bot should detect it and send messages
6. Check Railway logs to confirm

---

## Troubleshooting

### Issue: Bot not responding to messages
**Solution:**
- Make sure bot is added to all 3 groups
- Check group IDs are correct
- Verify tokens in Railway Variables
- Check Railway logs for errors

### Issue: Messages not sending
**Solution:**
- Make sure job posters have DMs enabled
- Check no Telegram rate limiting (wait 30 mins)
- Verify message variants look correct

### Issue: "Bot token is invalid"
**Solution:**
- Copy token from @BotFather again
- Make sure it's the correct bot
- Paste exactly (no spaces)

---

## You're Done! 🎉

Your bot is now:
✅ Running 24/7 on Railway  
✅ Listening to 3 groups  
✅ Auto-sending messages from 2 accounts  
✅ Tracking all jobs in JSON files  
✅ Rate-limited to avoid spam  

**Next time a job matching your skills is posted, the bot will automatically:**
1. Detect it ✅
2. Send Iklass message ✅
3. Wait 3-7 mins ✅
4. Send Abdul message ✅
5. Log everything ✅

**All hands-off!** 🤖

---

## Questions?

Check the full **RAILWAY_DEPLOYMENT.md** guide for more details on customization and monitoring.

