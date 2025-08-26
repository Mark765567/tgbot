from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
import datetime

TOKEN = "8208627039:AAED_N2sSXqUGaEl8ij-NuxQ76566I1jJW4"   # <-- put your BotFather token here
CHAT_ID = 376202431     # <-- replace with your Telegram chat ID

# Define your habits
TASKS = ["Homework", "Workout", "Read", "Play Chess"]

# Store progress in dictionary: { "08/25_Homework": "done" }
progress = {}

# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi Mark! I'll track your habits every day.\n"
        "Use /done <task> when you finish something.\n"
        "Try /test too!"
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("amen inch lava")

async def send_todo(context: ContextTypes.DEFAULT_TYPE):
    """Send daily to-do list automatically"""
    chat_id = context.job.chat_id
    date = datetime.date.today().strftime("%m/%d")
    tasks_list = "\n".join([f"⬜ {task}" for task in TASKS])
    await context.bot.send_message(chat_id, f"📅 {date} To-Do List:\n\n{tasks_list}")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark task as done"""
    if not context.args:
        await update.message.reply_text("Usage: /done task_name (example: /done Homework)")
        return

    task = " ".join(context.args).title()
    today = datetime.date.today().strftime("%m/%d")
    key = f"{today}_{task}"

    if task not in TASKS:
        await update.message.reply_text("❌ Task not found. Check spelling.")
        return

    progress[key] = "done"
    await update.message.reply_text(f"✅ Marked {task} as done for {today}")

async def weekly_report(context: ContextTypes.DEFAULT_TYPE):
    """Send report every Sunday 9PM"""
    chat_id = context.job.chat_id

    # Count stats
    total_tasks = len(TASKS) * 7
    done_tasks = 0
    task_count = {task: 0 for task in TASKS}

    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=6)

    for key, status in progress.items():
        date_str, task = key.split("_")
        month, day = map(int, date_str.split("/"))
        date = datetime.date(today.year, month, day)

        if date >= week_start and status == "done":
            done_tasks += 1
            task_count[task] += 1

    if done_tasks == 0:
        await context.bot.send_message(chat_id, "📊 No tasks logged this week.")
        return

    percent = round((done_tasks / total_tasks) * 100, 1)
    breakdown = "\n".join([f"{task}: {count}/7" for task, count in task_count.items()])

    report = (
        f"🎉 Congratulations Mark!\n"
        f"You did {done_tasks}/{total_tasks} tasks this week.\n"
        f"That’s {percent}%.\n\n📌 Breakdown:\n{breakdown}"
    )
    await context.bot.send_message(chat_id, report)

# --- Main ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("test", test))

    # Job queue for automatic messages
    job_queue = app.job_queue

    # Weekdays (Mon-Fri) → 6:40 & 8:00
    for t in [(6,40), (8,0)]:
        job_queue.run_daily(send_todo, time=datetime.time(t[0], t[1]), days=(0,1,2,3,4), chat_id=CHAT_ID)

    # Weekends (Sat-Sun) → 9:00 & 11:00
    for t in [(9,0), (11,0)]:
        job_queue.run_daily(send_todo, time=datetime.time(t[0], t[1]), days=(5,6), chat_id=CHAT_ID)

    # Sunday 9PM report
    job_queue.run_daily(weekly_report, time=datetime.time(21,0), days=(6,), chat_id=CHAT_ID)

    app.run_polling()

if __name__ == "__main__":
    main()
