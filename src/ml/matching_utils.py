import re

from src.telegram_bot.solr.solr_client import solr_get_vacancy

from django.utils.timezone import now


def search_vacancies(text: str) -> re.Match:
    """search for valid vacancy code(s) inside string parameter"""
    m = re.search("\w\d\d\d-\d{5,6}", text)

    return m


def get_valid_vacancy_code_from_str(text: str):
    m = search_vacancies(text)

    if m:
        vacancy = m.string[m.start(0):m.end(0)]
        return vacancy

    return None


def get_vacancy_document_from_str(text: str):
    """get vacancy document by searching for valid vacancy code inside string"""

    vacancy = get_valid_vacancy_code_from_str(text)

    if vacancy:
        # 2 - check if vacancy exists
        doc = solr_get_vacancy(vacancy)

        return doc
    return None


def get_valid_vacancy_document_from_str(text: str):
    """get vacancy document by searching for valid vacancy code inside string
    and if found check if vacancy is still valid
    returs tuple (document, int code) where code == 0 means success"""
    doc = get_vacancy_document_from_str(text)

    if doc:
        d = now()
        today_iso_date = f"{d.year:04d}{d.month:02d}{d.day:02d}"
        insert_date = str(doc['insertDate'][0])

        return (doc, 0) if insert_date == today_iso_date else (doc, 1)

    return None, 2




