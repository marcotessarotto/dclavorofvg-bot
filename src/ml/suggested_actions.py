

from src.backoffice.models import AiAction, UI_bot_help_message
from src.telegram_bot.ormlayer import CurrentUserContext, orm_get_all_sentences, orm_get_system_parameter

from src.telegram_bot.log_utils import main_logger as logger

"""
id	action	description
21	ASK_OR_VISIT_CPI	servizi erogati dai CPI/recarsi al CPI
9	BOT_CHOOSE_NEWS_CATEGORIES	come scelgo le categorie delle notizie col bot
8	BOT_HELP	
7	BOT_TUTORIAL	
29	BOT_WRONG_ANSWER	bot ha sbagliato risposta
18	CANNOT_SUBMIT_TO_VACANCY	non riesco a  candidarmi alla vacancy
19	CPI_OPENING_TIMES	orari apertura CPI
22	CPI_PHONE_NUMBER	quale è il numero del CPI ... ?
24	DOWNLOAD_MOBILE_APP	da dove scarico la app mobile?
16	ENABLE_ALL_NEWS_CATEGORIES	abilita tutte le categorie di notizie
6	GENERIC_MORE_INFO	generico, richiesta informazioni
12	GENERIC_WHERE_ASK_INFORMATION	dove posso chiedere info (generico)
5	GENERIC_WHO_CAN_I_CONTACT	generico
33	HELLO_BOT	
14	HOW_LONG_IS_COURSE	quanto dura il corso?
34	HOW_TO_CHANGE_AGE	vorrei cambiare la mia età
35	HOW_TO_CHANGE_STUDY_TITLE	vorrei cambiare il mio titolo di studio
4	HOW_TO_ENROLL	rispondi a "come si fa ad iscriversi?" / come mi candido
20	HOW_TO_SUBMIT_TO_VACANCY	come faccio a candidarmi ad una offerta di lavoro?
27	HOW_TO_SUBSCRIBE_TO_NEWSLETTER	come faccio ad iscrivermi alla newsletter?
23	MORE_INFO_ON_COURSES	più informazioni sui corsi di formazione
36	PUZZLING	incomprensibile :(
26	SEARCH_FOR_RECRUITING_DAY	ci sono recruiting in programma?
25	SEARCH_FOR_VACANCY	im interessa un lavoro da... ; a chi posso rivolgermi?
15	SHOW_LAST_NEWS	mostrami le (ultime) notizie
32	SHOW_LATEST_COURSES	Ci sono nuovi corsi ?
31	SHOW_LATEST_VACANCIES	Mandami le nuove offerte di lavoro
17	SHOW_PARTICULAR_NEWS_ITEM	mostrami una certa notizia
10	SHOW_VACANCIES	mostra/come visualizzare le offerte di lavoro
13	USER_DOES_NOT_UNDERSTAND	chiamare operatore umano?....
1	WHEN_IS_COURSE	rispondi a "quando si tiene il corso?"
28	WHEN_IS_EVENT	quando si tiene l'evento?
30	WHERE_IS_COMPETITION_NOTICE	Dove trovo il bando di concorso?
2	WHERE_IS_COURSE	rispondi a "dove si tiene il corso?"
3	WHO_ORGANIZES_COURSE	rispondi a "chi organizza il corso?"
11	WHO_TEACHES_COURSE	chi insegna al corso?

"""

_suggested_actions_dict = {}


def get_supported_actions():
    result = {}

    for k in _suggested_actions_dict:
        # result.append(k)

        sentences = orm_get_all_sentences(k)

        result[k] = sentences

    return result


def help_on_supported_ai_questions():

    library = get_supported_actions()
    result = 'Ad oggi, le domande a cui so rispondere :) sono:\n\n'

    for k,v in library.items():

        if v is None or len(v) == 0:
            continue

        # print(v)

        for s in v:
            result += "- " + s + "\n"

    # print(result)

    return result


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


def show_mobile_app_url(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}" con sicurezza pari al {int(confidence_perc)}%, ecco la mia risposta:\n\n'
        f'puoi scaricare la <a href="https://play.google.com/store/apps/details?id=it.insiel.ergonet.linksmt.applavoro">APP per Android da questo link</a>  \n'
        f'oppure la  <a href="https://itunes.apple.com/it/app/lavoro-fvg/id1327283831?mt=8">APP per iOS da questo link</a> ',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def show_last_news(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    # TODO: check if user has selected at least one category

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f'usa il comando /rimanda_ultime_notizie per rivedere le ultime notizie inviate.\n\n'
        f"Per ricevere le NUOVE notizie, non occorre che tu faccia niente! Te le mando io.\n"
        f"L'importante è che tu scelga le categorie di notizie che ti interessano ( con il comando /scegli ). "
        f"Ma penso che tu lo abbia già fatto :)",
        parse_mode='HTML'
    )


def show_offices_opening_times(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f"visita la seguente pagina per vedere gli orari dei Centri per l'Impiego: http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/lavoro/FOGLIA61/ ",
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def how_to_enroll(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    if current_context is None:
        update.message.reply_text(
            f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
            f"a cosa ti riferisci? un corso, un recruiting day, una offerta di lavoro.... prova a fare 'rispondi' sulla notizia che ti interessa e formula la tua domanda.",
            parse_mode='HTML'
        )
        return

    # TODO: recover informations from context

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f"ok, devo imparare a scoprire come si fa ad iscriversi in questo contesto ({current_context}) .... sto imparando a farlo :(",
        parse_mode='HTML'
    )


def send_bot_help(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n' +
        orm_get_system_parameter(UI_bot_help_message) +
        "\n\n" +
        help_on_supported_ai_questions(),
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def puzzling(update, context, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'mi dispiace, non riesco a capire che cosa mi stai dicendo :((( \n\n'
        f'prova a riformulare la domanda con altre parole oppure guarda i comandi disponibili con /aiuto',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


_suggested_actions_dict["ANS_WHEN_IS_COURSE"] = tell_when_is_event
_suggested_actions_dict["DOWNLOAD_MOBILE_APP"] = show_mobile_app_url
_suggested_actions_dict["SHOW_LAST_NEWS"] = show_last_news
_suggested_actions_dict["CPI_OPENING_TIMES"] = show_offices_opening_times
_suggested_actions_dict["HOW_TO_ENROLL"] = how_to_enroll
_suggested_actions_dict["BOT_HELP"] = send_bot_help
_suggested_actions_dict["PUZZLING"] = puzzling

# http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/lavoro/FOGLIA61/


def perform_suggested_action(update, context, telegram_user, current_context: CurrentUserContext, nss_result) -> str:

    suggested_action = nss_result["similarity_ws"][0]
    confidence = nss_result["similarity_ws"][1]

    logger.info(f"perform_suggested_action confidence={confidence}  suggested_action='{suggested_action}' current_context={current_context}")

    if suggested_action is None:
        suggested_action = ''

    od = nss_result["similarity_ws"][2]  # complete ordered dictionary of similarity results:
    #  {'0.5': ['<reference question>', '<ACTION>'], '0.16666666666666666': ['non capisco', 'USER_DOES_NOT_UNDERSTAND'],  ....

    if confidence <= 0.20:
        logger.warning("low confidence")

        # TODO: show different alternatives

    first_row_key = next(iter(od.keys()))  # i.e.  '0.5'
    first_row_values = next(iter(od.values()))  # i.e. ['<reference question>', '<ACTION>']
    # print(first_row_key)
    # print(first_row_values)

    confidence_perc = confidence * 100

    item = _suggested_actions_dict.get(suggested_action)

    if confidence <= 0.05:
        logger.warning("confidence too low, puzzling input by user")

        item = _suggested_actions_dict.get("PUZZLING")

    if item is None:
        logger.warning("perform_suggested_action: I don't know what to do!!!")
        return "-"

    item(update, context, current_context, first_row_values, confidence_perc)

    return f"answer by method {item.__name__}"

