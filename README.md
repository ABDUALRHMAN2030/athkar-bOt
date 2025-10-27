# Athkar Telegram Bot (Ready-to-Deploy)

This bot sends:
- Morning adhkar daily (06:00 Riyadh)
- Evening adhkar daily (18:00 Riyadh)
- Dhikr at 3:00 PM daily **except Friday**
- Dhikr at 9:00 PM daily
- Friday reminder for Surah Al-Kahf (09:00 Riyadh)
- Friday Asr dua at 3:00 PM Riyadh

## Quick Deploy on Render (Free)
1) Create a new repo on GitHub and upload all these files.
2) On Render.com → New → Blueprint → **Use render.yaml from your repo**.
3) Set environment variables on Render service:
   - `TG_TOKEN` = your bot token (from @BotFather)
   - `TG_CHAT_ID` = -1003180628364 (your channel ID)
4) Click **Deploy**. The worker starts and schedules jobs.
5) To test immediately, run `/ping` to your bot in DM, or check logs on Render.

> Your bot must be **admin** in the channel with permission to post messages.

## Optional: Images (Option C)
- If you place PNG images inside `assets/` with the following names, the bot will send them
  **after** the text message for that schedule. If a file is missing, it will just skip the image.
  - assets/morning.png
  - assets/evening.png
  - assets/three_pm.png
  - assets/nine_pm.png
  - assets/friday_kahf.png
  - assets/friday_asr.png

(You can design images yourself. The code does not generate Arabic text on images by default.)

## Local Run
```
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export TG_TOKEN=... ; export TG_CHAT_ID=-1003180628364
python main.py
```

## Timezone
All schedules run with `Asia/Riyadh` time via APScheduler.
