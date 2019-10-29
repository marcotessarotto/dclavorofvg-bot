from src.backoffice.definitions import UI_message_i_have_changed_your_categories, \
    UI_message_i_have_removed_all_your_categories
from src.telegram_bot.ormlayer import orm_get_telegram_user, orm_lookup_category_by_custom_command, \
    orm_get_category_group, orm_set_telegram_user_categories, orm_get_categories
from src.telegram_bot.user_utils import check_user_privacy_approval


def _get_category_status(update, context, custom_telegram_command):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    category = orm_lookup_category_by_custom_command(custom_telegram_command)

    if category is None:
        return

    queryset = telegram_user.categories.filter(key=category.key)

    if len(queryset) == 0:
        return False
    else:
        return True


def _change_categories(update, context, category_group_name):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    group = orm_get_category_group(category_group_name)

    if group is None:
        print("_change_categories - category group '" + category_group_name + "' is not defined")
        return

    telegram_user = orm_set_telegram_user_categories(update.message.chat.id, group.categories)

    update.message.reply_text(
        UI_message_i_have_changed_your_categories + telegram_user.categories_str(),
        parse_mode='HTML'
    )


def _set_all_categories(update, context, add_or_remove_all: bool):
    telegram_user = orm_get_telegram_user(update.message.from_user.id)

    if check_user_privacy_approval(telegram_user, update, context):
        # privacy not yet approved by user
        return

    if add_or_remove_all:
        queryset = orm_get_categories()

        telegram_user = orm_set_telegram_user_categories(update.message.chat.id, queryset)

        update.message.reply_text(
            UI_message_i_have_changed_your_categories + telegram_user.categories_str(),
            parse_mode='HTML'
        )
    else:
        telegram_user = orm_set_telegram_user_categories(update.message.chat.id, None)

        update.message.reply_text(
            UI_message_i_have_removed_all_your_categories,
            parse_mode='HTML'
        )