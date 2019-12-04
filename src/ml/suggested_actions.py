

from src.backoffice.models import AiAction
from src.telegram_bot.ormlayer import CurrentUserContext

from src.telegram_bot.log_utils import main_logger as logger

"""
21	ASK_OR_VISIT_CPI	servizi erogati dai CPI/recarsi al CPI
20	HOW_TO_SUBMIT_TO_VACANCY	come faccio a candidarmi ad una offerta di lavoro?
19	CPI_OPENING_TIMES	orari apertura CPI
18	CANNOT_SUBMIT_TO_VACANCY	non riesco a  candidarmi alla vacancy
17	SHOW_PARTICULAR_NEWS_ITEM	mostrami una certa notizia
16	ENABLE_ALL_NEWS_CATEGORIES	abilita tutte le categorie di notizie
15	SHOW_LAST_NEWS	mostrami le (ultime) notizie
14	ANS_HOW_LONG_IS_COURSE	quanto dura il corso?
13	USER_DOES_NOT_UNDERSTAND	chiamare operatore umano?....
12	GENERIC_WHERE_ASK_INFORMATION	dove posso chiedere info (generico)
11	ANS_WHO_TEACHES_COURSE	chi insegna al corso?
10	SHOW_VACANCIES	mostra/come visualizzare le offerte di lavoro
9	BOT_CHOOSE_NEWS_CATEGORIES	come scelgo le categorie delle notizie col bot
8	BOT_HELP	
7	BOT_TUTORIAL	
6	GENERIC_MORE_INFO	generico, richiesta informazioni
5	GENERIC_WHO_CAN_I_CONTACT	generico
4	ANS_HOW_TO_ENROLL	rispondi a "come si fa ad iscriversi?"
3	ANS_WHO_ORGANIZES_COURSE	rispondi a "chi organizza il corso?"
2	ANS_WHERE_IS_COURSE	rispondi a "dove si tiene il corso?"
1	ANS_WHEN_IS_COURSE	rispondi a "quando si tiene il corso?"
"""

_suggested_actions_dict = {}


def tell_when_is_event(update, context, current_context: CurrentUserContext, row, *args, **kwargs):
    if current_context is None:
        logger.warning("current_context is None")
        return

    if current_context.item is None:
        logger.warning("current_context.item is None")
        return

    if current_context.item.when_question is None:
        logger.warning("current_context.item.when_question is None")
        return



    pass


def show_mobile_app_url(update, context, current_context: CurrentUserContext, row, *args, **kwargs):
    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f'puoi scaricare la <a href="https://play.google.com/store/apps/details?id=it.insiel.ergonet.linksmt.applavoro">APP per Android da questo link</a>  \n'
        f'oppure la  <a href="https://itunes.apple.com/it/app/lavoro-fvg/id1327283831?mt=8">APP per iOS da questo link</a> ',
        parse_mode='HTML'
    )


def show_last_news(update, context, current_context: CurrentUserContext, row, *args, **kwargs):
    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f'usa il comando /rimanda_ultime_notizie per rivedere le ultime notizie inviate.\n\n'
        f"Per ricevere le NUOVE notizie, non occorre che tu faccia niente! Te le mando io.\n"
        f"L'importante è che tu scelga le categorie di notizie che ti interessano ( con il comando /scegli ). Ma penso che tu lo abbia già fatto :)",
        parse_mode='HTML'
    )


_suggested_actions_dict["ANS_WHEN_IS_COURSE"] = tell_when_is_event
_suggested_actions_dict["DOWNLOAD_MOBILE_APP"] = show_mobile_app_url
_suggested_actions_dict["SHOW_LAST_NEWS"] = show_last_news


def perform_suggested_action(update, context, telegram_user, current_context: CurrentUserContext, nss_result) -> str:

    suggested_action = nss_result["similarity_ws"][0]
    confidence = nss_result["similarity_ws"][1]

    if suggested_action is None:
        suggested_action = ''

    od = nss_result["similarity_ws"][2]  # dictionary

    # if current_context is None:
    #     return None

    print(current_context)
    print(od)

    first_row = next(iter(od.values()))
    print(first_row)

    item = _suggested_actions_dict.get(suggested_action)
        # current_context.current_ai_context.action)

    if item is None:
        return "mi dispiace....non capisco e/o non so cosa fare.";

    item(update, context, current_context, first_row)

    return
