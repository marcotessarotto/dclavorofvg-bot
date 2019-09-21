
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ForceReply
)

from .ormlayer import *


def news(update, context):
    """ Invia un nuovo articolo """

    folder_new = 'demo_new'

    fd = open(folder_new + '/category', 'r')
    cat = fd.read()[:-1]

    fd = open(folder_new + '/title', 'r')
    title = fd.read()[:-1]

    fd = open(folder_new + '/body', 'r')
    body = fd.read()

    fd = open(folder_new + '/link', 'r')
    link = fd.read()
    fd.close()

    news_item = orm_add_newsitem(title, body, link)
    context.user_data['news_id'] = news_item.news_id

    # Costruzione della descrizione
    caption = '<b>' + str(news_item.title) + \
              ' [' + news_item.news_id + ']</b>\n'

    text = news_item.text.split()
    caption += str(" ".join(text[:30]))

    # Aggiunta del link per approfondire
    caption += '... <a href=\"' + news_item.link + '\">continua</a>'

    context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=open(folder_new + '/allegato_1.jpg', 'rb'),
        caption=caption,
        parse_mode='HTML'
    )

    # Attivazione tastiera con pulsanti 'like' e 'dislike'
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Ti è piaciuto l'articolo?",
        reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    text=u'\u2717',
                    callback_data='feedback - ' + news_item.news_id
                ),
                InlineKeyboardButton(
                    text=u'\u2713',
                    callback_data='feedback + ' + news_item.news_id
                )
        ]])
    )


def callback_feedback(update, data):
    """ Gestisce i feedback sugli articoli """

    feed = data[0]
    news_id = data[1]
    orm_add_feedback(feed, news_id)

    update.callback_query.edit_message_text(
        text='Grazie per il feedback!\n',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text='Commenta',
                callback_data='comment ' + news_id)]
        ])
    )


def callback_comment(update, context, news_id):
    """ Gestisce i commenti agli articoli """

    update.callback_query.edit_message_text(
        'Grazie per il feedback!'
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='Commento art. ' + news_id,
        reply_markup=ForceReply()
    )


def comment(update, context):

    reply = update.message.reply_to_message.text.split()
    text = update.message.text
    orm_add_comment(text, reply[2], update.message.from_user.id)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Commento caricato con successo!'
    )
