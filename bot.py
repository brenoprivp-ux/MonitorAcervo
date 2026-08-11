import os
import sqlite3
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "stats.db")
BOT_TOKEN = os.environ["BOT_TOKEN"]
GROUP_CHAT_ID = int(os.environ["GROUP_CHAT_ID"])
RANKING_INTERVAL_SECONDS = 48 * 60 * 60  # 48 horas


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS stats (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            photos INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0
        )"""
    )
    conn.commit()
    conn.close()


def upsert_media(user_id: int, username: str, is_photo: bool = False, is_video: bool = False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM stats WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        if is_photo:
            c.execute("UPDATE stats SET photos = photos + 1, username=? WHERE user_id=?", (username, user_id))
        if is_video:
            c.execute("UPDATE stats SET videos = videos + 1, username=? WHERE user_id=?", (username, user_id))
    else:
        c.execute(
            "INSERT INTO stats (user_id, username, photos, videos) VALUES (?, ?, ?, ?)",
            (user_id, username, 1 if is_photo else 0, 1 if is_video else 0),
        )
    conn.commit()
    conn.close()


def get_ranking():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT username, photos, videos, (photos + videos) AS total "
        "FROM stats WHERE (photos + videos) > 0 ORDER BY total DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def reset_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM stats")
    conn.commit()
    conn.close()


def format_ranking_text(rows) -> str:
    if not rows:
        return "📊 Nenhuma mídia enviada nas últimas 48h."

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 *Ranking de mídias (acumulado)*", ""]
    for i, (username, photos, videos, total) in enumerate(rows, start=1):
        prefix = medals[i - 1] if i <= 3 else f"{i}º"
        lines.append(f"{prefix} {username} — 📷 {photos} | 🎥 {videos} | Total: {total}")
    return "\n".join(lines)


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_CHAT_ID:
        return

    msg = update.effective_message
    user = update.effective_user
    username = f"@{user.username}" if user.username else user.first_name

    if msg.photo:
        upsert_media(user.id, username, is_photo=True)
    if msg.video:
        upsert_media(user.id, username, is_video=True)


async def post_ranking_job(context: ContextTypes.DEFAULT_TYPE):
    rows = get_ranking()
    text = format_ranking_text(rows)
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text, parse_mode="Markdown")
    # Contagem é cumulativa: não reseta após postar.
    # Use /resetranking manualmente se quiser zerar o placar algum dia.


async def ranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra o ranking atual sem resetar os contadores (checagem manual)."""
    if update.effective_chat.id != GROUP_CHAT_ID:
        return
    rows = get_ranking()
    text = format_ranking_text(rows)
    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def resetranking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reseta manualmente os contadores (admin)."""
    if update.effective_chat.id != GROUP_CHAT_ID:
        return
    reset_stats()
    await update.effective_message.reply_text("✅ Contadores zerados manualmente.")


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(CommandHandler("ranking", ranking_command))
    app.add_handler(CommandHandler("resetranking", resetranking_command))

    app.job_queue.run_repeating(
        post_ranking_job,
        interval=RANKING_INTERVAL_SECONDS,
        first=RANKING_INTERVAL_SECONDS,
        name="ranking_48h",
    )

    logger.info("Bot iniciado. Postando ranking a cada 48h no chat %s", GROUP_CHAT_ID)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
