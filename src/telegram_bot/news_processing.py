import datetime
import mimetypes

import time

from src.telegram_bot.log_utils import news_logger as logger, benchmark_decorator

from src.gfvgbo.settings import MEDIA_ROOT

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from src.backoffice.definitions import (
    DATE_FORMAT_STR,
    UI_message_show_complete_news_item,
    UI_broadcast_message,
    SHOW_CATEGORIES_IN_NEWS,
    UI_message_news_item_category,
    UI_message_request_for_news_item_feedback,
    UI_news,
    UI_message_published_on,
    UI_external_link,
    UI_message_read_news_item, UI_message_this_is_audio_version_of_news_item, SHOW_READ_COMMAND_IN_NEWS_BODY,
    CURRENT_CONTEXT, UI_message_news_item_is_useful, UI_message_news_item_is_not_useful)

from src.backoffice.models import NewsItem, TelegramUser

from src.telegram_bot.ormlayer import orm_get_fresh_news_to_send, orm_get_system_parameter, orm_get_all_telegram_users, \
    orm_log_news_sent_to_user, orm_inc_telegram_user_number_received_news_items, orm_get_news_item, \
    orm_has_user_seen_news_item, orm_find_ai_action, orm_find_ai_context, orm_update_telegram_user, \
    orm_set_current_user_context
from src.telegram_bot.print_utils import my_print

# dictionary of file_id cache, used when uploading files to telegram server
from src.telegram_bot.text_to_speech_utils import text_to_speech

file_id_cache_dict = {}


@benchmark_decorator
def news_dispatcher(context: CallbackContext):
    """news_dispatcher is called periodically by the bot's job_queue to check if there are news item to send to users"""
    list_of_news = orm_get_fresh_news_to_send()

    # now = datetime.datetime.now()

    if len(list_of_news) == 0:
        logger.info("news_dispatcher - nothing to do")
        return
    else:
        logger.info(f"news_dispatcher - there are news to process: {len(list_of_news)}")

    all_telegram_users = orm_get_all_telegram_users()

    for news_item in list_of_news:

        if len(news_item.categories.all()) == 0 and news_item.broadcast_message is not True:  # do not process news item with no categories specified
            continue

        logger.debug(f"news_dispatcher - elaboration of news item id={news_item.id}")

        for telegram_user in all_telegram_users:

            if not telegram_user.enabled:
                continue

            intersection_result = intersection(news_item.categories.all(), telegram_user.categories.all())

            if news_item.broadcast_message is not True and len(intersection_result) == 0:
                continue

            # send this news_item to this telegram_user
            send_news_to_telegram_user(context, news_item, telegram_user, intersection_result, request_feedback=news_item.ask_like_dislike_to_user)

        news_item.processed = True
        from django.utils.timezone import now
        news_item.processed_timestamp = now()

        news_item.save()

        # observed issue: sending two (or more news item) with feeback; it has happended that
        # all feedback messages are shown after all the news item messages (lost association
        # between news item and feedback message); add a delay in order to allow telegram to send messages in order
        time.sleep(1)  # sleep 1 second

    logger.info("news_dispatcher - complete")


def _send_file_using_mime_type(
        context,
        _telegram_user_id: int,
        _file_path,
        _file_mime_type: str,
        caption=None,
        reply_markup=None,
):
    if caption is None:
        caption = ''

    if len(caption) > 1024:
        logger.warn("WARNING! len(caption) cannot be > 1024, truncating...")
        caption = caption[:1021] + '...'

    if _file_mime_type is None:
        _file_mime_type = mimetypes.guess_type(_file_path)[0]

    _file_id = _get_file_id_for_file_path(_file_path)  # is file already present on Telegram servers?

    if _file_mime_type == 'image/gif':
        _message = context.bot.send_animation(
            chat_id=_telegram_user_id,
            animation=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            parse_mode='HTML',
            reply_markup=reply_markup,
        )
    elif _file_mime_type.startswith('image'):
        _message = context.bot.send_photo(
            chat_id=_telegram_user_id,
            photo=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    elif _file_mime_type.startswith('application'):
        _message = context.bot.send_document(
            chat_id=_telegram_user_id,
            document=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    elif _file_mime_type == 'audio/ogg':
        _message = context.bot.send_voice(
            chat_id=_telegram_user_id,
            voice=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    elif _file_mime_type == 'video/mp4':
        _message = context.bot.send_video(
            chat_id=_telegram_user_id,
            video=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    elif _file_mime_type.startswith('audio'):
        _message = context.bot.send_audio(
            chat_id=_telegram_user_id,
            audio=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        _message = context.bot.send_document(
            chat_id=_telegram_user_id,
            document=_file_id if _file_id is not None else open(_file_path, 'rb'),
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

    _lookup_file_id_in_message(_message, _file_path, _file_id)


def send_news_as_audio_file(context,
                            news_id: int,
                            telegram_user: TelegramUser,
                            reply_markup=None):
    news_item = orm_get_news_item(news_id)
    if news_item is None:
        return False

    fname = text_to_speech(news_item, news_item.title)

    _send_file_using_mime_type(
        context,
        telegram_user.user_id,
        fname,
        None,
        caption=UI_message_this_is_audio_version_of_news_item.format(news_id),
        reply_markup=reply_markup,
    )


@benchmark_decorator
def send_news_to_telegram_user(
        context,
        news_item: NewsItem,
        telegram_user: TelegramUser,
        intersection_result=None,
        request_feedback=True,
        title_only=False,
        news_item_already_shown_to_user=False,
        produce_content_only=False  # if True, produce and return html content and do not send messages (works only for title_only=True)
):
    if not telegram_user.has_accepted_privacy_rules:
        return

    if telegram_user.has_user_blocked_bot:
        return

    if telegram_user.user_id < 0:  # do not send news item to a group
        return

    logger.info(
        f"send_news_to_telegram_user - news_item={news_item.id}, telegram_user={telegram_user.user_id}")

    # keyboard with 'like' and 'dislike' buttons
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton(  # like button
            text='👍 ' + UI_message_news_item_is_useful,
            callback_data=f'feedback + {news_item.id}  {news_item.ask_comment_to_user}'
        ),
        InlineKeyboardButton(  # dislike button
            text='👎 ' + UI_message_news_item_is_not_useful,
            callback_data=f'feedback - {news_item.id}  {news_item.ask_comment_to_user}'
        ),
    ]]) if request_feedback else None

    telegram_user_id = telegram_user.user_id

    if news_item.context:
        current_ai_context = news_item.context
    else:
        current_ai_context = orm_find_ai_context('NEWS')

    orm_set_current_user_context(telegram_user_id, current_ai_context, news_item)

    # title_html_content = ''
    categories_html_content = ''
    body_html_content = ''
    link_html_content = ''

    # see also: https://core.telegram.org/bots/api#html-style
    # cannot embed <b> inside <a> tag

    if news_item.processed and news_item.processed_timestamp is not None:
        processed_timestamp_html = ' ' + UI_message_published_on + ' ' + news_item.processed_timestamp.strftime(DATE_FORMAT_STR)
    else:
        processed_timestamp_html = ''

    news_id_block = f"[{UI_news} #{news_item.id}{processed_timestamp_html}]"

    # title/header
    if news_item.title_link is not None and not title_only:
        title_html_content = f'<a href="{news_item.title_link}">{news_id_block} {news_item.title}</a>\n'
    else:
        title_html_content = f'<b>{news_id_block} {news_item.title}</b>\n'

    show_categories_in_news = SHOW_CATEGORIES_IN_NEWS

    # optional: show categories
    if show_categories_in_news is True:
        if intersection_result is not None and len(intersection_result) > 0:
            # print(intersection_result)
            categories_html_content = f'<i>{UI_message_news_item_category}: '

            for cat in intersection_result:
                categories_html_content += cat.name + ','

            categories_html_content = categories_html_content[:-1]

            categories_html_content += '</i>\n'
        else:
            s = ''
            for cat in news_item.categories.all():
                s += cat.name + ','

            if len(s) > 0:
                s = s[:-1]
                categories_html_content = f'<i>{UI_message_news_item_category}: {s}</i>\n'

        if news_item.broadcast_message is True:
            categories_html_content += f'<i>{UI_broadcast_message}</i>\n'

    #  title_only == True: used by resend_last_processed_news_command_handler
    if title_only:

        # if news item has no text, do not show the 'show news' command
        # if news_item.text is None:
        #     html_news_content = title_html_content + categories_html_content
        # else:
        html_news_content = title_html_content + categories_html_content + UI_message_show_complete_news_item.format(
            news_item.id)

        # append text showing command for reading title of news
        if SHOW_READ_COMMAND_IN_NEWS_BODY and telegram_user.is_text_to_speech_enabled:
            html_news_content += "\n" + UI_message_read_news_item.format(news_item.id)

        delta = len(html_news_content) - 1024

        if delta > 0:  # text is too long; we enforce length limit even if using send_message
            reduced_len = len(title_html_content) - delta - 3  # -3 is for the '...' string

            html_news_content = title_html_content[
                                :reduced_len] + '...' + categories_html_content + UI_message_show_complete_news_item.format(
                news_item.id)

            # append text showing command for reading title of news
            if SHOW_READ_COMMAND_IN_NEWS_BODY and telegram_user.is_text_to_speech_enabled:
                html_news_content += "\n" + UI_message_read_news_item.format(news_item.id)

            logger.warning("html_news_content too long, has been truncated")

        if produce_content_only:
            return html_news_content

        if telegram_user.is_text_to_speech_enabled:

            fname = text_to_speech(news_item, news_item.title)

            _send_file_using_mime_type(
                context,
                telegram_user.user_id,
                fname,
                None,
                caption=html_news_content,
                reply_markup=reply_markup
            )
        else:
            context.bot.send_message(
                chat_id=telegram_user.user_id,
                text=html_news_content,
                reply_markup=reply_markup,
                parse_mode='HTML',
                disable_web_page_preview=news_item.disable_web_page_preview
            )

        return

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

            if len(body_html_content) < len(news_text):
                body_html_content += '...'

    # optional link
    if news_item.link is not None:
        if news_item.link_caption is not None:
            link_html_content = f' <a href=\"{news_item.link}\">{news_item.link_caption}</a>'
        else:
            link_html_content = f' <a href=\"{news_item.link}\">{UI_external_link}</a>'

    # complete html body of news item (separate from title. link...)
    html_news_content = title_html_content + categories_html_content + body_html_content + link_html_content

    # logger.info(f"send_news_to_telegram_user - len(html_content) = {len(html_news_content)}")
    # logger.info(f"send_news_to_telegram_user - html_content =  {html_news_content}")

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
        logger.info(f"send_news_to_telegram_user - fs path of file1: {file_path}")

        file_mime_type = mimetypes.guess_type(file_path)[0]
        logger.info(f"file1 mime_type: {file_mime_type}")

        file1_is_image = file_mime_type.startswith('image')
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
                    reply_markup=reply_markup,
                    parse_mode='HTML',
                    disable_web_page_preview=news_item.disable_web_page_preview
                )
            else:

                _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type,
                                           caption=html_news_content, reply_markup=reply_markup,)

        else:  # file1 is present but it is not an image
            # first, send content of news item
            context.bot.send_message(
                chat_id=telegram_user_id,
                text=html_news_content,
                reply_markup=reply_markup,
                parse_mode='HTML',
                disable_web_page_preview=news_item.disable_web_page_preview
            )

            # file1 is defined but it is not an image, send it as a document
            _send_file_using_mime_type(context, telegram_user_id, file_path, file_mime_type)

    else:  # file1 is not defined, send only content of news item
        context.bot.send_message(
            chat_id=telegram_user.user_id,
            text=html_news_content,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=news_item.disable_web_page_preview
        )

    if news_item.file2 is not None:
        file_path = MEDIA_ROOT + news_item.file2.file_field.name
        logger.info(f"send_news_to_telegram_user - fs path of file2 to send: {file_path}")

        _send_file_using_mime_type(context, telegram_user_id, file_path, _file_mime_type=None)

    if news_item.file3 is not None:
        file_path = MEDIA_ROOT + news_item.file3.file_field.name
        logger.info(f"send_news_to_telegram_user - fs path of file3 to send: {file_path}")

        _send_file_using_mime_type(context, telegram_user_id, file_path, _file_mime_type=None)

    # if request_feedback:
    #
    #     time.sleep(0.1)  # sleep for 100 ms, to be sure that previous message has been sent
    #
    #     logger.info(f"send_news_to_telegram_user - context.bot.send_message chat_id={telegram_user.user_id}")
    #     context.bot.send_message(
    #         chat_id=telegram_user.user_id,
    #         text=UI_message_request_for_news_item_feedback,
    #         reply_markup=reply_markup,
    #         disable_notification=True
    #     )

    # we record this activity only once (if the news item has already been shown to user, do not log this activity)
    if not news_item_already_shown_to_user:
        orm_log_news_sent_to_user(news_item, telegram_user)

    orm_inc_telegram_user_number_received_news_items(telegram_user)


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
        except (AttributeError, IndexError) as e:
            try:
                _file_id = message.audio.file_id
            except AttributeError:
                try:
                    _file_id = message.animation.file_id
                except (AttributeError, IndexError) as e:
                    try:
                        _file_id = message.animation[0].file_id
                    except (AttributeError, IndexError, TypeError) as e:
                        try:
                            _file_id = message.voice.file_id
                        except (AttributeError, IndexError) as e:
                            try:
                                _file_id = message.video.file_id
                            except (AttributeError, IndexError) as e:
                                logger.info("_process_message_lookup_file_id: cannot find file_id")
                                my_print(message, 4)
                                return

    if _file_id is not None:
        file_id_cache_dict[_file_path] = _file_id

        logger.info(f"process_message_for_file_id: found {_file_id} for {_file_path}")
    else:
        logger.warning(f"process_message_for_file_id: _file_id NOT found for {_file_path}")

    return


def _get_file_id_for_file_path(_file_path):
    return file_id_cache_dict.get(_file_path)


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def show_news_by_id(context, news_id: int, telegram_user: TelegramUser):
    """show a specific news item to user"""
    news_item = orm_get_news_item(news_id)
    if news_item is None:
        return False

    news_item_already_shown_to_user = orm_has_user_seen_news_item(telegram_user, news_item)
    send_news_to_telegram_user(
        context,
        news_item,
        telegram_user,
        request_feedback=not news_item_already_shown_to_user and news_item.ask_like_dislike_to_user,
        news_item_already_shown_to_user=news_item_already_shown_to_user
    )

    return True
