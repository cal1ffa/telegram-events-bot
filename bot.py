import logging
import csv
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ===== ВСТАВЬТЕ СВОЙ ТОКЕН =====
TOKEN = '8994488546:AAHOPhCkT7bSkOnR6dX5TxqNRLueV1LYCDM'
CSV_FILE = 'events.csv'

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ===== ФУНКЦИЯ ЧТЕНИЯ МЕРОПРИЯТИЙ =====
def get_events_by_date(target_date):
    events = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['date'] == target_date:
                    events.append(f"⏰ {row['time']} | {row['name']}\n📍 {row['place']}")
    except FileNotFoundError:
        return ["❌ Ошибка: файл events.csv не найден"]
    if not events:
        return ["✅ На эту дату мероприятий нет"]
    return events

# ===== КЛАВИАТУРА =====
def get_keyboard():
    buttons = [
        [KeyboardButton("📅 Сегодня"), KeyboardButton("📆 Завтра")],
        [KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ===== КОМАНДЫ БОТА =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Привет! Я бот мероприятий!\n\n"
        "Команды:\n"
        "/today - сегодня\n"
        "/tomorrow - завтра\n"
        "/events 2026-05-20 - на конкретную дату\n\n"
        "Или жми на кнопки 👇",
        reply_markup=get_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Команды:\n"
        "/today - мероприятия на сегодня\n"
        "/tomorrow - на завтра\n"
        "/events 2026-05-20 - на конкретную дату\n"
        "Пример: /events 2026-06-12"
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_str = datetime.now().strftime("%Y-%m-%d")
    events = get_events_by_date(today_str)
    await update.message.reply_text(f"📅 *Сегодня, {today_str}*\n\n" + "\n\n".join(events), parse_mode="Markdown")

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tomorrow_date = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow_date.strftime("%Y-%m-%d")
    events = get_events_by_date(tomorrow_str)
    await update.message.reply_text(f"📆 *Завтра, {tomorrow_str}*\n\n" + "\n\n".join(events), parse_mode="Markdown")

async def events_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Пример: /events 2026-05-20")
        return
    date_str = context.args[0]
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except:
        await update.message.reply_text("❌ Неверный формат. Используй ГГГГ-ММ-ДД")
        return
    events = get_events_by_date(date_str)
    await update.message.reply_text(f"📌 *{date_str}*\n\n" + "\n\n".join(events), parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📅 Сегодня":
        await today(update, context)
    elif text == "📆 Завтра":
        await tomorrow(update, context)
    elif text == "❓ Помощь":
        await help_command(update, context)
    else:
        await update.message.reply_text("Используй /help для команд или кнопки")

# ===== ЗАПУСК =====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("tomorrow", tomorrow))
    app.add_handler(CommandHandler("events", events_by_date))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()