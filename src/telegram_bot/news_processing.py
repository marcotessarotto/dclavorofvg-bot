import datetime
import mimetypes

from src.gfvgbo.settings import MEDIA_ROOT

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from src.backoffice.definitions import DATE_FORMAT_STR, param_show_match_category_news, UI_broadcast_message, \
    UI_request_for_news_item_feedback
from src.backoffice.models import NewsItem, TelegramUser


from src.telegram_bot.ormlayer import orm_get_fresh_news_to_send, orm_get_system_parameter, orm_get_all_telegram_users, \
    orm_log_news_sent_to_user, orm_inc_telegram_user_number_received_news_items
from src.telegram_bot.print_utils import my_print


def news_dispatcher(context: CallbackContext):

    a = datetime.datetime.now()

    list_of_news = orm_get_fresh_news_to_send()

    debug_send_news = (orm_get_system_parameter("DEBUG_SEND_NEWS").lower() == "true")
    if debug_send_news:
        print("DEBUG_SEND_NEWS = " + str(debug_send_news))

    now = datetime.datetime.now()

    if len(list_of_news) == 0:
        print("news_dispatcher - nothing to do " + str(now))
        return
    else:
        print("news_dispatcher - there are news to process: " + str(len(list_of_news)))

    all_telegram_users = orm_get_all_telegram_users()

    for news_item in list_of_news:

        print("news_dispatcher - elaboration of news item id=" + str(news_item.id))

        for telegram_user in all_telegram_users:

            if not telegram_user.enabled:
                continue

            intersection_result = intersection(news_item.categories.all(), telegram_user.categories.all())

            if news_item.broadcast_message is not True and len(intersection_result) == 0:
                continue

            # send this news to this telegram_user
            send_news_to_telegram_user(context, news_item, telegram_user, intersection_result)

        news_item.processed = True
        from django.utils.timezone import now
        news_item.processed_timestamp = now()
        if not debug_send_news:
            news_item.save()

    b = datetime.datetime.now()

    c = b - a

    print("news_dispatcher - finished processing all news - dt=" + str(c.microseconds) + " microseconds")


def _send_file_using_mime_type(context, _telegram_user_id: int, _file_path, _file_mime_type: str, caption=None):
    if caption is None:
        caption = ''

    if len(caption) > 1024:
        print("WARNING! len(caption) cannot be > 1024, truncating...")
        caption = caption[:1024]

    if _file_mime_type is None:
        _file_mime_type = mimetypes.guess_type(_file_path)[0]

    _file_id = _get_file_id_for_file_path(_file_path)  # is file already present on Telegram servers?

    if _file_mime_type == 'image/gif':
        _message = context.bot.send_animation(
            chat_id=_telegram_user_id,
            animation=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    elif _file_mime_type.startswith('image'):
        _message = context.bot.send_photo(
            chat_id=_telegram_user_id,
            photo=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    elif _file_mime_type.startswith('application'):
        _message = context.bot.send_document(
            chat_id=_telegram_user_id,
            document=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    elif _file_mime_type == 'audio/ogg':
        _message = context.bot.send_voice(
            chat_id=_telegram_user_id,
            voice=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    elif _file_mime_type == 'video/mp4':
        _message = context.bot.send_video(
            chat_id=_telegram_user_id,
            video=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    elif _file_mime_type.startswith('audio'):
        _message = context.bot.send_audio(
            chat_id=_telegram_user_id,
            audio=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )
    else:
        _message = context.bot.send_document(
            chat_id=_telegram_user_id,
            document=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML'
        )

    _lookup_file_id_in_message(_message, _file_path, _file_id)


def send_news_to_telegram_user(context, news_item : NewsItem, telegram_user: TelegramUser, intersection_result=None, request_feedback=True,
                               title_only=False, ask_comment=False):
    print(
        "send_news_to_telegram_user - news_item=" + str(news_item.id) + ", telegram_user=" + str(telegram_user.user_id))

    telegram_user_id = telegram_user.user_id

    a = datetime.datetime.now()

    # title_html_content = ''
    categories_html_content = ''
    body_html_content = ''
    link_html_content = ''

    # see also: https://core.telegram.org/bots/api#html-style
    # cannot embed <b> inside <a> tag

    if news_item.processed and news_item.processed_timestamp is not None:
        processed_timestamp_html = ' ' + news_item.processed_timestamp.strftime(DATE_FORMAT_STR)
    else:
        processed_timestamp_html = ''

    # title/header
    if news_item.title_link is not None:
        title_html_content = '<a href="' + news_item.title_link + '"> ' + \
                             str(news_item.title) + \
                             ' [' + str(news_item.id) + ']' + processed_timestamp_html + \
                                                        ' </a>\n'
    else:
        title_html_content = '<b>' + str(news_item.title) + \
                             ' [' + str(news_item.id) + ']' + processed_timestamp_html + '</b>\n'

    show_categories_in_news = orm_get_system_parameter(param_show_match_category_news).lower() == "true"

    # optional: show categories
    if show_categories_in_news is True:
        if intersection_result is not None:
            # print(intersection_result)
            categories_html_content = '\n<i>'

            for cat in intersection_result:
                categories_html_content += cat.name + ','

            categories_html_content = categories_html_content[:-1]

            categories_html_content += '</i>\n'
        elif news_item.broadcast_message is True:
            categories_html_content = '\n<i>' + UI_broadcast_message + '</i>\n'

    # news body
    news_text = news_item.text

    if news_text is not None:
        if news_item.show_all_text:
            body_html_content = news_text
        else:
            text = news_text.split()

            number_of_words = news_item.show_first_n_words
            if number_of_words < 0:
                number_of_words = 30

            body_html_content = str(" ".join(text[:number_of_words]))

    # optional link
    if news_item.link is not None:
        link_html_content = '... <a href=\"' + news_item.link + '\">' + news_item.link_caption + '</a>'

    # complete html body of news item (separate from title. link...)
    html_news_content = title_html_content + categories_html_content + body_html_content + link_html_content

    print("send_news_to_telegram_user - len(html_content) = " + str(len(html_news_content)))

    # print("len(title_html_content) = " + str(len(title_html_content)))
    # print("len(categories_html_content) = " + str(len(categories_html_content)))
    # print("len(body_html_content) = " + str(len(body_html_content)))
    # print("len(link_html_content) = " + str(len(link_html_content)))

    file1_is_image = False
    # file_id = None  # is file already present on Telegram servers?

    # file1 is present, check if it is an image
    if news_item.file1 is not None:
        # print(news_item.file1.file_field.name)
        # example: uploads/2019/10/03/500px-Tux_chico.svg_VtRyDrN.png

        file_path = MEDIA_ROOT + news_item.file1.file_field.name

        print("send_news_to_telegram_user - fs path of file1: " + file_path)

        file_mime_type = mimetypes.guess_type(file_path)[0]

        file1_is_image = file_mime_type.startswith('image')

        print("file1 mime_type: " + str(file_mime_type))
        # print("file1_is_image: " + str(file1_is_image))

        # file_id = _get_file_id_for_file_path(file_path)
        # print("file_id on telegram server: " + str(file_id))

        if file1_is_image:

            # LIMIT on caption len: 1024 bytes! or we get MEDIA_CAPTION_TOO_LONG from Telegram
            # https://core.telegram.org/bots/api#sendphoto

            if len(html_news_content) > 1024:
                # first, send image associated with news item
                _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type)

                # second, send content of news item
                context.bot.send_message(
                    chat_id=telegram_user_id,
                    text=html_news_content,
                    parse_mode='HTML'
                )
            else:

                _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type, caption=html_news_content)

        else:  # file1 is present but it is not an image
            # first, send content of news item
            context.bot.send_message(
                chat_id=telegram_user_id,
                text=html_news_content,
                parse_mode='HTML'
            )

            # file1 is defined but it is not an image, send it as a document
            _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type)

    else: # file1 is not defined, send only content of news item
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=html_news_content,
            parse_mode='HTML'
        )

    if news_item.file2 is not None:
        file_path = MEDIA_ROOT + news_item.file2.file_field.name
        print("send_news_to_telegram_user - fs path of file2 to send: " + file_path)

        _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type=None)

    if news_item.file3 is not None:
        file_path = MEDIA_ROOT + news_item.file3.file_field.name
        print("send_news_to_telegram_user - fs path of file3 to send: " + file_path)

        _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type=None)

    # keyboard with 'like' and 'dislike' buttons
    if request_feedback:
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=orm_get_system_parameter(UI_request_for_news_item_feedback),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(  # dislike button
                    text=u'\u2717',
                    callback_data='feedback - ' + str(news_item.id) + ' ' + str(ask_comment)
                ),
                InlineKeyboardButton(  # like button
                    text=u'\u2713',
                    callback_data='feedback + ' + str(news_item.id) + ' ' + str(ask_comment)
                )
            ]])
        )

    orm_log_news_sent_to_user(news_item, telegram_user)

    orm_inc_telegram_user_number_received_news_items(telegram_user)

    b = datetime.datetime.now()

    c = b - a

    print("send_news_to_telegram_user - dt=" + str(c.microseconds) + " microseconds")


def _lookup_file_id_in_message(message, _file_path: str, file_id):
    """search for file_id in message, if parameter file_id is not None;
    if found, store it in file_id cache (associate it to file_path)"""
    if file_id is not None:
        return

    _file_id = None
    # Python community recommend a strategy of "easier to ask for forgiveness than permission" (EAFP) rather than "look before you leap" (LBYL)
    # https://stackoverflow.com/a/610923/974287
    try:
        _file_id = message.document.file_id
    except AttributeError:
        try:
            # if message.photo is not None:
            _file_id = message.photo[0].file_id
        except AttributeError:
            print("_process_message_lookup_file_id: cannot find file_id")
            my_print(message, 4)
            return

    if _file_id is not None:
        file_id_cache_dict[_file_path] = _file_id

    print("process_message_for_file_id: " + str(_file_id) + " for " + _file_path)

    return


def _get_file_id_for_file_path(_file_path):
    return file_id_cache_dict.get(_file_path)


# dictionary of file_id cache, used when uploading files to telegram server
file_id_cache_dict = {}


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3