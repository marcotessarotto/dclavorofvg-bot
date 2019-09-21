
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from .ormlayer import (
    orm_add_user,
    update_user_category_settings
)

from django_project.backoffice.definitions import get_categories_dict

category = get_categories_dict()


def choose(update, context):
    """ Permette all'utente di scegliere tra le categorie disponibili """

    user = orm_add_user(update.message.from_user)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Seleziona una o più categorie:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
    )


def inline_keyboard(user):
    """ Costruisce la inline_keyboard in base alle categorie già scelte """

    result = []

    for index in category.keys():

        queryset = user.categories.filter(key=index)

        label = str(category[index][0])
        if len(queryset) != 0:
            label = u' \u2737  ' + label.upper() + u' \u2737'

        result.append([InlineKeyboardButton(
            text=label,
            callback_data='choose ' + index)]
        )

    # Inserisce il pulsante 'CHIUDI'
    result.append(
        [InlineKeyboardButton(text='CHIUDI', callback_data='choose OK')]
    )

    return result


def callback_choice(update, scelta):
    user = orm_add_user(update.callback_query.from_user)

    if scelta == 'OK':  # 'OK'  Stampa le categorie scelte
        cat_scelte = ''
        for index in category.keys():
            queryset = user.categories.filter(key=index)

            if len(queryset) != 0:
                cat_scelte += '- ' + category[index][0] + \
                              '  ' + category[index][1] + '\n'

        # ALERT: Non è stata scelta alcuna categoria!
        if cat_scelte == '':
            update.callback_query.answer(
                text='Non è stata scelta alcuna categoria!',
                show_alert=True
            )
            return

        update.callback_query.edit_message_text(
            text='Ok, le categorie sono state impostate con successo. '
                 'Hai scelto:\n\n' + cat_scelte +
                 '\nDigita /scegli per modificare.'
        )

    else:  # Toggle checked/unchecked per la categoria selezionata
        update_user_category_settings(user, scelta)

        update.callback_query.edit_message_text(
            text="Seleziona una o più categorie:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard(user))
        )
