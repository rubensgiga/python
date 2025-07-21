from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import datetime
import random
import logging

BOT_TOKEN = "7081150298:AAET-CUC2OsIElP6n2kDDihM-v6HGt-ybPo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DATABASE_NAME = "sensei.db"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        logger.info(f"Подключение к базе данных {DATABASE_NAME} выполнено")
    except sqlite3.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER,
            date TEXT,
            status TEXT
        )
        """)
        conn.commit()
        logger.info("Таблица 'progress' создана (или уже существовала)")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы: {e}")

conn = create_connection()  # Создаем подключение при запуске
if conn is not None:
    create_table(conn)
else:
    logger.critical("Не удалось подключиться к базе данных. Бот не будет работать.")
    exit()

MOTIVATION = [
    "Слабость — это выбор. Как и сила.",
    "Ты либо куют тебя, либо ты ржавеешь.",
    "Нет вдохновения? Работай. Оно придёт позже.",
    "Истина проста: дисциплина > вдохновение.",
    "Если не ты — то кто? Если не сейчас — то когда?"
]

PUNISHMENT = [
    "Ты подвёл себя. Встань. Исправь.",
    "Страдание очищает. Завтра — вдвойне.",
    "Молчание — позор. Действие — путь.",
    "Хочешь быть гением? Терпи. И делай.",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Пользователь {user.id} ({user.username}) запустил команду /start")
    await update.message.reply_text(
        f"⚔️ Привет, воин {user.first_name or user.username or 'Неизвестный'}. Я — Сэнсей. Готов следовать Пути?\n\n"
        "Команды:\n"
        "/я_готов — начать день\n"
        "/отчет <текст> — отправь результат\n"
        "/пропустил — пропуск дня\n"
        "/накажи — дисциплина\n"
        "/статус — посмотреть путь\n"
        "/клятва — услышать её снова"
    )

async def ya_gotov(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    date = str(datetime.date.today())
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO progress (user_id, date, status) VALUES (?, ?, ?)", (user_id, date, "✔"))
        conn.commit()
        await update.message.reply_text("✅ День принят. Действуй. Сенсей смотрит.")
        logger.info(f"Пользователь {user_id} отметил день как 'я готов'")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при записи в базу данных: {e}")
        await update.message.reply_text("❌ Ошибка при записи в базу данных. Попробуйте позже.")

async def otchet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    user_id = update.effective_user.id
    if not text:
        await update.message.reply_text("Напиши свой отчёт после команды, воин.")
        return
    try:
        # Можно дополнительно сохранять отчёты, если нужно
        await update.message.reply_text("📝 Отчёт принят. Твоя дисциплина крепнет.")
        logger.info(f"Пользователь {user_id} отправил отчет: {text[:50]}...")
    except Exception as e:
        logger.error(f"Ошибка при обработке отчета: {e}")
        await update.message.reply_text("❌ Ошибка при обработке отчета. Попробуйте позже.")

async def propustil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    date = str(datetime.date.today())
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO progress (user_id, date, status) VALUES (?, ?, ?)", (user_id, date, "❌"))
        conn.commit()
        await update.message.reply_text("❌ Слабо, воин. Завтра будь лучше.")
        logger.info(f"Пользователь {user_id} отметил день как 'пропустил'")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при записи в базу данных: {e}")
        await update.message.reply_text("❌ Ошибка при записи в базу данных. Попробуйте позже.")

async def nakazhi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(PUNISHMENT)
    await update.message.reply_text(f"🔥 {quote}")
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запросил 'наказание'")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM progress WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        total = len(rows)
        success = sum(1 for r in rows if r[0] == "✔")
        fail = sum(1 for r in rows if r[0] == "❌")
        await update.message.reply_text(f"📊 Дней пройдено: {success}\n❌ Сорвано: {fail}\n📅 Всего: {total}")
        logger.info(f"Пользователь {user_id} запросил статус")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при чтении из базы данных: {e}")
        await update.message.reply_text("❌ Ошибка при чтении из базы данных. Попробуйте позже.")

async def klyatva(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧬 *Клятва ученика Пути:*\n\n"
        "Я клянусь пребывать в дисциплине.\n"
        "Клянусь быть гением каждый день.\n"
        "Клянусь идти к свету, несмотря на боль.\n"
        "Сенсей — свидетель моей воли.",
        parse_mode="Markdown"
    )
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запросил 'клятву'")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # Здесь исправлено: регистрация всех команд без ошибок
    app.add_handler(CommandHandler("я_готов", ya_gotov))
    app.add_handler(CommandHandler("отчет", otchet))
    app.add_handler(CommandHandler("пропустил", propustil))
    app.add_handler(CommandHandler("накажи", nakazhi))
    app.add_handler(CommandHandler("статус", status))
    app.add_handler(CommandHandler("клятва", klyatva))

    logger.info("⚙️ Бот Сенсей запущен...")
    app.run_polling()
