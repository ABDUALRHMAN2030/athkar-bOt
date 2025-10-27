import os
import asyncio
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")  # e.g. -1003180628364
TIMEZONE = "Asia/Riyadh"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_text(file_name: str) -> str:
    path = os.path.join(BASE_DIR, "messages", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

async def maybe_send_image(app, filename: str):
    path = os.path.join(BASE_DIR, "assets", filename)
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "rb") as img:
                await app.bot.send_photo(chat_id=CHAT_ID, photo=img)
    except Exception as e:
        # Log but don't crash the job
        print(f"[warn] send_photo failed for {filename}: {e}")

async def send_text_and_optional_image(app, text_file: str, image_file: str):
    text = read_text(text_file)
    await app.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML", disable_web_page_preview=True)
    await maybe_send_image(app, image_file)

async def job_morning(app):
    await send_text_and_optional_image(app, "morning.txt", "morning.png")

async def job_evening(app):
    await send_text_and_optional_image(app, "evening.txt", "evening.png")

async def job_three_pm(app):
    await send_text_and_optional_image(app, "three_pm.txt", "three_pm.png")

async def job_nine_pm(app):
    await send_text_and_optional_image(app, "nine_pm.txt", "nine_pm.png")

async def job_friday_kahf(app):
    await send_text_and_optional_image(app, "friday_kahf.txt", "friday_kahf.png")

async def job_friday_asr(app):
    await send_text_and_optional_image(app, "friday_asr.txt", "friday_asr.png")

# Command handlers
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive ✅")

async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Current time in {TIMEZONE}: {now}")

async def main():
    assert TG_TOKEN, "TG_TOKEN env var is required"
    assert CHAT_ID, "TG_CHAT_ID env var is required"
    app = Application.builder().token(TG_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("now", now))

    # Scheduler
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # Morning: daily 06:00 Riyadh
    scheduler.add_job(lambda: asyncio.create_task(job_morning(app)),
                      CronTrigger(hour=6, minute=0))
    # Evening: daily 18:00 Riyadh
    scheduler.add_job(lambda: asyncio.create_task(job_evening(app)),
                      CronTrigger(hour=18, minute=0))
    # 3 PM daily except Friday (Sun,Mon,Tue,Wed,Thu,Sat); In CronTrigger, 0=Mon...6=Sun by default in APScheduler.
    # We'll use day_of_week with names for clarity (mon-sun). Exclude fri.
    scheduler.add_job(lambda: asyncio.create_task(job_three_pm(app)),
                      CronTrigger(day_of_week="mon,tue,wed,thu,sat,sun", hour=15, minute=0))
    # 9 PM daily
    scheduler.add_job(lambda: asyncio.create_task(job_nine_pm(app)),
                      CronTrigger(hour=21, minute=0))
    # Friday Surah Al-Kahf: Friday 09:00 Riyadh
    scheduler.add_job(lambda: asyncio.create_task(job_friday_kahf(app)),
                      CronTrigger(day_of_week="fri", hour=9, minute=0))
    # Friday Asr dua: Friday 15:00 Riyadh
    scheduler.add_job(lambda: asyncio.create_task(job_friday_asr(app)),
                      CronTrigger(day_of_week="fri", hour=15, minute=0))

    scheduler.start()

    print("Scheduler started ✓")
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
