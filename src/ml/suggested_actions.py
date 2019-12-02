

from src.backoffice.models import AiAction
from src.telegram_bot.ormlayer import CurrentUserContext

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


def tell_when_is_event(update, context, current_context: CurrentUserContext):

    pass


_suggested_actions_dict["ANS_WHEN_IS_COURSE"] = tell_when_is_event


def perform_suggested_action(update, context, telegram_user, current_context: CurrentUserContext, nss_result) -> str:

    if current_context is None:
        return None

    # item = _suggested_actions_dict.get(current_context.current_ai_context.action)
    #
    # if item is None:
    #     return "mi dispiace....non capisco e/o non so cosa fare.";
    #
    # item(update, context, )

    pass