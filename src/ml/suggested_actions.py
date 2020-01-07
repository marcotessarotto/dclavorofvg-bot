from src.backoffice.definitions import SHOW_SUPPORTED_AI_QUESTIONS
from src.backoffice.models import AiAction, UI_bot_help_message
from src.ml.matching_utils import search_vacancies, get_valid_vacancy_document_from_str, get_valid_vacancy_code_from_str
from src.telegram_bot.ormlayer import CurrentUserContext, orm_get_all_sentences, orm_get_system_parameter

from src.telegram_bot.log_utils import main_logger as logger
from src.telegram_bot.solr.solr_client import solr_get_vacancy

from django.utils.timezone import now


_suggested_actions_dict = {}


def get_supported_actions():
    result = {}

    for k in _suggested_actions_dict:
        # result.append(k)

        sentences = orm_get_all_sentences(k)

        result[k] = sentences

    return result


def help_on_supported_ai_questions(show_random_questions=False, max_number_of_questions_to_show=6):

    library = get_supported_actions()
    result = 'Ad oggi, alcune delle domande a cui so rispondere :) sono:\n\n'

    if show_random_questions:
        import random
        rnd_list = []

        for iter in range(5):
            r = random.randint(0, len(library)-1)
            if r not in rnd_list:
                rnd_list.append(r)

        # rnd_list = [random.randint(0, len(library)-1) for iter in range(5)]

        key_list = [k for k in library.keys()]

        def do_it(result):
            counter = 0
            for i in rnd_list:
                k = key_list[i]
                v = library[k]

                if v is None or len(v) == 0:
                    continue

                for s in v:
                    result += "- " + s + "\n"

                    counter += 1

                    if counter >= max_number_of_questions_to_show:
                        return result

            return result

        result = do_it(result)

    else:  # show all supported questions

        for k, v in library.items():

            if v is None or len(v) == 0:
                continue

            # print(v)

            for s in v:
                result += "- " + s + "\n"

    # print(result)

    return result


def tell_when_is_event(update, context, message_text, current_context: CurrentUserContext, row, *args, **kwargs):
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


def show_mobile_app_url(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}" con sicurezza pari al {int(confidence_perc)}%, ecco la mia risposta:\n\n'
        f'puoi scaricare la <a href="https://play.google.com/store/apps/details?id=it.insiel.ergonet.linksmt.applavoro">APP per Android da questo link</a>  \n'
        f'oppure la  <a href="https://itunes.apple.com/it/app/lavoro-fvg/id1327283831?mt=8">APP per iOS da questo link</a> ',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def show_last_news(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    # TODO: check if user has selected at least one category

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f'usa il comando /rimanda_ultime_notizie per rivedere le ultime notizie inviate.\n\n'
        f"Per ricevere le NUOVE notizie, non occorre che tu faccia niente! Te le mando io.\n"
        f"L'importante è che tu scelga le categorie di notizie che ti interessano ( con il comando /scegli ). "
        f"Ma penso che tu lo abbia già fatto :)",
        parse_mode='HTML'
    )


def show_offices_opening_times(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f"visita la seguente pagina per vedere gli orari dei Centri per l'Impiego: http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/lavoro/FOGLIA61/ ",
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def how_to_enroll(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    if current_context is None:
        update.message.reply_text(
            f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
            f"a cosa ti riferisci? un corso, un recruiting day, una offerta di lavoro.... prova a fare 'rispondi' sulla notizia che ti interessa e formula la tua domanda.",
            parse_mode='HTML'
        )
        return

    # TODO: recover informations from context

    # VACANCY? rispondere con app mobile, sito web

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n'
        f"ok, devo imparare a scoprire come si fa ad iscriversi in questo contesto ({current_context}) .... sto imparando a farlo :(",
        parse_mode='HTML'
    )


def send_bot_help(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    show_supported_ai_questions = orm_get_system_parameter(SHOW_SUPPORTED_AI_QUESTIONS) == "True"

    if show_supported_ai_questions:
        additional_help = "\n\n" + help_on_supported_ai_questions()
    else:
        additional_help = ""

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco la mia risposta:\n\n' +
        orm_get_system_parameter(UI_bot_help_message) + additional_help,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def puzzling(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'mi dispiace, non riesco a capire che cosa mi stai dicendo :((( \n\n'
        f'prova a riformulare la domanda con altre parole oppure guarda i comandi disponibili con /aiuto',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def search_engine(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):

    update.message.reply_text(
        f'per cercare un testo nelle notizie, puoi usare il comando /cerca',
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def vacancy_issues(update, context, message_text, current_context: CurrentUserContext, row, confidence_perc, *args, **kwargs):
    # 1 - identify vacancy code: i.e. C957-28472
    # regexp_ \w\d\d\d-\d{5,6}

    vacancy_code = get_valid_vacancy_code_from_str(message_text)

    if not vacancy_code:
        answer = "se vuoi, prova a dirmi il codice completo dell'offerta di lavoro su cui hai problemi " \
                 "o vuoi avere maggiori informazioni, ad esempio:\n" \
                 "'ho problemi con l'offerta di lavoro L424-12345'"
    else:
        # user has written a valid vacancy code
        # let's check if vacancy exists and is still valid

        doc, code = get_valid_vacancy_document_from_str(vacancy_code)

        if doc:  # in case code == 0 or code == 1
            email_contact = doc.get("email")
            contact_type = doc.get("tipoContatto")
            reference = doc.get("riferimento")

        def get_email_info():
            # email_contact is a list
            if bool(email_contact):
                return f"<b>Per chiedere informazioni o aiuto su questa offerta di lavoro, " \
                          f"ti consiglio di scrivere a {email_contact[0]} oppure a comunicazione.lavoro@regione.fvg.it</b>\n"
            else:
                return f"<b>Per chiedere informazioni o aiuto su questa offerta di lavoro, " \
                          f"ti consiglio di scrivere a comunicazione.lavoro@regione.fvg.it</b>\n"

        if doc and code == 0:  # valid vacancy found

            answer = f"mi risulta che l'offerta di lavoro {vacancy_code} sia pubblicata e valida.\n"

            # reference is a list; so the following line is equivalent to: 'if reference and len(reference) > 0:'
            if bool(reference):
                answer += f"il riferimento risulta essere '{reference[0]}'.\n"

            if bool(contact_type):
                answer += f"la modalità di contatto è '{contact_type[0]}'.\n"

            # 3 - check if email field exists
            answer += get_email_info()

            answer += "In caso di problemi tecnici quando provi a candidarti online, contatta il numero verde di Insiel 800098788\n"

        elif code == 1:  # old vacancy found
            answer = "purtroppo l'offerta di lavoro che mi hai indicato ({vacancy_code}) è scaduta o è stata rimossa :(\n"

            answer += get_email_info()

        else:  # no vacancy found
            email_contact = None
            contact_type = None
            reference = None

            answer = f"hai specificato l'offerta di lavoro {vacancy_code} ma non ho trovato nessuna offerta, neanche tra quelle scadute.\n" \
                     f"Controlla se hai scritto il codice offerta giusto :|\n"

    update.message.reply_text(
        f'ho interpretato la tua domanda come "{row[0]}", ecco qua la mia risposta:\n\n' +
        answer,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


# "in caso di problemi tecnici, contatta il numero verde di Insiel 800xxxxxxx " \
# "oppure scrivi a comunicazione.lavoro@regione.fvg.it"


_suggested_actions_dict["ANS_WHEN_IS_COURSE"] = tell_when_is_event
_suggested_actions_dict["DOWNLOAD_MOBILE_APP"] = show_mobile_app_url
_suggested_actions_dict["SHOW_LAST_NEWS"] = show_last_news
_suggested_actions_dict["CPI_OPENING_TIMES"] = show_offices_opening_times
_suggested_actions_dict["HOW_TO_ENROLL"] = how_to_enroll
_suggested_actions_dict["BOT_HELP"] = send_bot_help
_suggested_actions_dict["PUZZLING"] = puzzling
_suggested_actions_dict["VACANCY_ISSUE"] = vacancy_issues
_suggested_actions_dict["HOW_TO_SUBMIT_TO_VACANCY"] = vacancy_issues
_suggested_actions_dict["SEARCH_ENGINE"] = search_engine

# http://www.regione.fvg.it/rafvg/cms/RAFVG/formazione-lavoro/lavoro/FOGLIA61/


def perform_suggested_action(update, context, telegram_user, current_context: CurrentUserContext, message_text, nss_result) -> str:

    suggested_action = nss_result["similarity_ws"][0]
    confidence = nss_result["similarity_ws"][1]

    logger.info(f"perform_suggested_action confidence={confidence}  suggested_action='{suggested_action}' current_context={current_context}")

    if suggested_action is None:
        suggested_action = ''

    od = nss_result["similarity_ws"][2]  # complete ordered dictionary of similarity results:
    #  {'0.5': ['<reference question>', '<ACTION>'], '0.16666666666666666': ['non capisco', 'USER_DOES_NOT_UNDERSTAND'],  ....

    # if confidence < 50% and context is defined, lookup the best nss_result with matching context
    if confidence < 0.5 and current_context and current_context.current_ai_context:
        context = current_context.current_ai_context.context

        for k, v in od.items():
            if v[2] != context:
                # print("skip!")
                continue

            first_row_key = k
            first_row_values = v
            confidence = float(k)

            break

        logger.info(f"perform_suggested_action: new first_row_key={first_row_key}, first_row_values={first_row_values}")

    if confidence <= 0.20:
        logger.warning("low confidence")

        # TODO: show different alternatives

    first_row_key = next(iter(od.keys()))  # i.e.  '0.5'
    first_row_values = next(iter(od.values()))  # i.e. ['<reference question>', '<ACTION>']
    # print(first_row_key)
    # print(first_row_values)

    confidence_perc = confidence * 100

    item = _suggested_actions_dict.get(suggested_action)

    if confidence <= 0.10:
        logger.warning("confidence too low, puzzling input by user")

        item = _suggested_actions_dict.get("PUZZLING")

    if item is None:
        logger.warning("perform_suggested_action: I don't know what to do!!!")
        return "-"

    item(update, context, message_text, current_context, first_row_values, confidence_perc)

    return f"answer by method {item.__name__}"

