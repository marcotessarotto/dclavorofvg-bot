import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, AIORateLimiter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('start')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context)
    print(context.args)

    text_caps = ' '.join(context.args).upper() if context.args else 'No text provided'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


if __name__ == '__main__':

    from pathlib import Path
    token_file = Path('token.txt')

    if not token_file.exists():
        token_file = Path('../../token.txt')

    token = os.environ.get('TOKEN') or open(token_file).read().strip()

    # application = ApplicationBuilder().token(token).build()
    # application = ApplicationBuilder().token(token).rate_limiter(MyLimiter()).build()

    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    application = ApplicationBuilder().token(token).rate_limiter(AIORateLimiter()).build()

    start_handler = CommandHandler('start', start)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    caps_handler = CommandHandler('caps', caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    application.run_polling()
