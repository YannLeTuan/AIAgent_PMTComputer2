import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent
from app.core.config import settings


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Xin chào, tôi là chatbot của PMT Computer.\n"
        "Tôi có thể hỗ trợ tra cứu đơn hàng, sản phẩm, bảo hành, đổi trả và thông tin cửa hàng."
    )
    await update.message.reply_text(text)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session_store.clear_session(chat_id)
    await update.message.reply_text("Đã xóa ngữ cảnh hội thoại của phiên chat này.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    chat_id = str(update.effective_chat.id)

    history = session_store.get_history(chat_id)
    context_state = session_store.get_context(chat_id)

    result = await asyncio.to_thread(
    chat_with_agent,
    user_text,
    history,
    context_state,
    chat_id
)

    session_store.set_history(chat_id, result["history"])
    session_store.set_context(chat_id, result["context_state"])

    await update.message.reply_text(result["answer"])


def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("Chưa có TELEGRAM_BOT_TOKEN trong .env")

    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot đang chạy...")
    app.run_polling()


if __name__ == "__main__":
    main()