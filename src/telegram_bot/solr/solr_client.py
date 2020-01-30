import time

from SolrClient import SolrClient
from django.utils.timezone import now

from src.telegram_bot.ormlayer import orm_get_obj_from_cache, orm_set_obj_in_cache

from src.gfvgbo.secrets import SOLR_HOST, SOLR_PORT

# solr = SolrClient(f"http://{SOLR_HOST}:{SOLR_PORT}/solr")


def _get_solr_client():
    return SolrClient(f"http://{SOLR_HOST}:{SOLR_PORT}/solr")


def solr_get_professional_categories():
    result = orm_get_obj_from_cache("solr_get_professional_categories")

    if result:
        return result

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': 'categoriaProfessionale:*',
        'facet': True,
        'facet.field': 'categoriaProfessionale_str',
    })

    dict = res.get_facets()

    od = dict['categoriaProfessionale_str']

    od = {i: od[i] for i in sorted(od.keys(), reverse=False)}  # sort dict by key

    orm_set_obj_in_cache("solr_get_professional_categories", od, timeout=60*60*12)

    return od


def solr_get_professional_categories_today():
    result = orm_get_obj_from_cache("solr_get_professional_categories_today")

    if result:
        return result

    d = now()
    today_iso_date = f"{d.year:04d}{d.month:02d}{d.day:02d}"

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': f'categoriaProfessionale:* AND insertDate:{today_iso_date}',
        'facet': True,
        'facet.field': 'categoriaProfessionale_str',
    })

    dict = res.get_facets()

    od = dict['categoriaProfessionale_str']

    orm_set_obj_in_cache("solr_get_professional_categories_today", od, timeout=60*60*1)

    return od


def solr_get_professional_profile():
    result = orm_get_obj_from_cache("solr_get_professional_profile")

    if result:
        return result

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': 'profiloProfessionale:*',
        'facet': True,
        'facet.field': 'profiloProfessionale_str',
    })

    dict = res.get_facets()

    od = dict['profiloProfessionale_str']

    od = {i: od[i] for i in sorted(od.keys(), reverse=False)}  # sort dict by key

    orm_set_obj_in_cache("solr_get_professional_profile", od, timeout=60*60*12)

    return od


def solr_get_professional_profile_today():
    result = orm_get_obj_from_cache("solr_get_professional_profile_today")

    if result:
        return result

    d = now()
    today_iso_date = f"{d.year:04d}{d.month:02d}{d.day:02d}"

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': f'profiloProfessionale:* AND insertDate:{today_iso_date}',
        'facet': True,
        'facet.field': 'profiloProfessionale_str',
    })

    dict = res.get_facets()

    od = dict['profiloProfessionale_str']

    orm_set_obj_in_cache("solr_get_professional_profile_today", od, timeout=60*60*1)

    return od


def solr_get_vacancy(vacancy_id: str):

    if not vacancy_id:
        return None

    vacancy_id = vacancy_id.upper()

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': f'id:{vacancy_id}',
    })

    documents = res.data['response']['docs']

    if len(documents) == 0:
        return None
    else:
        return documents[0]


def solr_search_vacancies(search_str: str):  # WIP

    d = now()
    today_iso_date = f"{d.year:04d}{d.month:02d}{d.day:02d}"

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': f'profiloProfessionale:{search_str} AND insertDate:{today_iso_date}',
    })

    documents = res.data['response']['docs']

    if len(documents) == 0:
        return None
    else:
        return documents


def solr_vacancies_published_today():

    d = now()
    today_date = f"{d.day:02d}/{d.month:02d}/{d.year:04d}"

    solr = _get_solr_client()

    res = solr.query('bot_core', {
        'q': f'dataInizioValidita:"{today_date}"',
    })

    documents = res.data['response']['docs']

    return documents


