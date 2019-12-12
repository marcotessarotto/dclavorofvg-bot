import time

from SolrClient import SolrClient
from django.utils.timezone import now

from src.telegram_bot.ormlayer import orm_get_obj_from_cache, orm_set_obj_in_cache

solr = SolrClient('http://10.4.100.2:8983/solr')


def solr_get_professional_categories():
    result = orm_get_obj_from_cache("solr_get_professional_categories")

    if result:
        return result

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

    if not str:
        return None

    solr = SolrClient('http://10.4.100.2:8983/solr')
    res = solr.query('bot_core', {
        'q': f'id:{vacancy_id}',
    })

    documents = res.data['response']['docs']

    if len(documents) == 0:
        return None
    else:
        return documents[0]
