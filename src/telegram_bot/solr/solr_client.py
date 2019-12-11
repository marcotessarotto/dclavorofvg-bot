import time

from SolrClient import SolrClient

from src.telegram_bot.ormlayer import orm_get_obj_from_cache, orm_set_obj_in_cache

solr = SolrClient('http://10.4.100.2:8983/solr')


def solr_get_professional_categories():
    result = orm_get_obj_from_cache("solr_get_professional_categories")

    if result:
        return result

    res = solr.query('bot_core', {
        'q': 'categoriaProfessionale:*',
        'facet': True,
        'facet.field': 'categoriaProfessionale',
    })

    dict = res.get_facets()

    od = dict['categoriaProfessionale']

    words_to_be_removed = ('ed', 'e', 'alla', 'varie')

    for w in words_to_be_removed:
        od.pop(w)

    orm_set_obj_in_cache("solr_get_professional_categories", od, timeout=60*60*12)

    return od


def solr_get_vacancy(vacancy_id: str):

    solr = SolrClient('http://10.4.100.2:8983/solr')
    res = solr.query('bot_core', {
        'q': f'id:{vacancy_id}',
    })

    documents = res.data['response']['docs']

    if len(documents) == 0:
        return None
    else:
        return documents[0]
