import time
from functools import wraps

from treetaggerwrapper import TreeTagger
from nltk.corpus import wordnet as wn

import cherrypy
import json

from treetaggerwrapper import TreeTagger

from src.telegram_bot.log_utils import ws_logger as logger, log_user_input, debug_update

from src.backoffice.models import *

from multiprocessing import Process

# reference_sentence = "Come posso fare per avere più informazioni?"

reference_sentences = [
    ("come posso fare per avere più informazioni?", "MORE_INFO"),
    ("a chi posso chiedere informazioni?", "MORE_INFO_WHO"),
    ("dove posso chiedere informazioni?", "MORE_INFO_WHERE"),
    ("come mi iscrivo?", "HOW_TO_ENROLL"),
    ("quando si tiene l'evento?", "WHEN_IS_EVENT"),
    ("quando ci sarà l'evento?", "WHEN_IS_EVENT"),
    ("quando si tiene il corso?", "WHEN_IS_COURSE"),
    ("quando ci sarà il corso?", "WHEN_IS_COURSE"),
    ("chi tiene il corso?","WHO_IS_COURSE_ORGANIZER"),
    ("chi organizza il corso?","WHO_IS_COURSE_ORGANIZER"),
    ("mi sono perso","HELP"),
    ("non capisco","HELP"),
    ("maggiori informazioni","MORE_INFO_GENERAL"),
    ("chi posso contattare","MORE_INFO_CONTACT"),
    ("ho bisogno di una mano","HELP"),
    ("non capisco","HELP"),
    ("esiste un tutorial","HELP_TUTORIAL"),
    ("aiuto con i comandi del bot","HELP_BOT_COMMANDS"),
    ("come scelgo le categorie?","HELP_CHOOSE_NEWS_CATEGORIES"),
    ("voglio più informazioni sui comandi","HELP_BOT_COMMANDS"),
    ("dove sono le offerte di lavoro?","HELP_JOB_OFFERS"),
    ("in che linguaggio è scritto il bot","HELP_BOT_DEV"),
    ("info comandi bot","HELP_BOT_COMMANDS"),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
    ("", ""),
]

tagbuildopt = {}
tagbuildopt["TAGDIR"] = '/opt/bot/treetagger'
tagbuildopt["TAGLANG"] = "it"
tagger = TreeTagger(**tagbuildopt)


def my_benchmark_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):

        # a = datetime.now()
        # https://stackoverflow.com/a/49667269/974287
        # time.time_ns requires python >= 3.7
        a = time.time_ns()

        try:
            return func(*args, **kwargs)
        finally:
            # b = datetime.now()
            b = time.time_ns()

            c = b - a
            print(f"{func.__name__} dt={c / 1000000} milliseconds")

    return wrapped


def process_sentence(sentence):
    dict = {}

    tagger_result = tagger.tag_text(sentence)
    result = []

    for s in tagger_result:
        w = s.split('\t')

        if w[1] != 'PON':
            result.append(w)

    for row in result:
        word = row[2]
        # print(f"analysis of word '{word}'")

        # http://www.nltk.org/howto/wordnet.html
        synsets = wn.synsets(word, lang="ita")

        dict[word] = synsets

    return dict


def calc_dict_average(d):

    if len(d) == 0:
        return 0

    res = 0
    for k1, v1 in d.items():
        if v1:
            res += v1

    res = res / len(d)

    return res


def compare_sentences(d1, d2, lch_similarity=False):

    dict = {}

    for k1,v1 in d1.items():  # v1 is a list

        maxval = 0
        # best_match = None
        maxpos = 0

        for synset1 in v1:

            for k2, v2 in d2.items():

                pos = 0

                for synset2 in v2:

                    if lch_similarity:
                        v = synset1.lch_similarity(synset2)
                    else:
                        v = synset1.path_similarity(synset2)

                    if v and v > maxval:
                        maxval = v
                        # best_match = synset2
                        maxpos = pos

                    pos = pos + 1

        calc_maxval = maxval
        if maxpos > 0:
            calc_maxval = calc_maxval / maxpos

        # print(f"max similarity between '{k1}' and sentence: max={maxval}, calc_maxval={calc_maxval}, best_match={best_match}, maxpos={maxpos}")

        dict[k1] = calc_maxval

    return calc_dict_average(dict), dict


@my_benchmark_decorator
def find_most_similar_sentence(sentence):
    """returns most similar sentence: confidence and string value"""

    confidence = 0
    result = None
    confidence_sentence = None

    d2 = process_sentence(sentence)

    rdict = {}

    for row in reference_sentences:
        ref_sentence = row[0]
        ref_target = row[1]

        if ref_sentence is None or len(ref_sentence) == 0:
            continue

        d1 = process_sentence(ref_sentence)

        r1 = compare_sentences(d1, d2)
        r2 = compare_sentences(d2, d1)

        val = (r1[0] + r2[0]) / 2.

        rdict[val] = (ref_sentence,ref_target)

        if val > confidence:
            confidence = val
            result = ref_target
            confidence_sentence = ref_sentence

    sorted_dict = {i: rdict[i] for i in sorted(rdict.keys(), reverse=True)}  # sort dict by key value in reverse order

    print(f"find_most_similar_sentence(): confidence={confidence} result={result} sentence={sentence} confidence_sentence={confidence_sentence}")

    return result, confidence, sorted_dict


# find_most_similar_sentence("dove mi trovo?")
#
# find_most_similar_sentence("maggiori info")
#
# find_most_similar_sentence("maggiori informazioni")
#
# find_most_similar_sentence("a chi posso chiedere?")
#
# find_most_similar_sentence("a chi posso telefonare?")
#
# find_most_similar_sentence("a chi posso mandare una email?")
#
# find_most_similar_sentence("a chi posso chiedere chiarimenti su dove si terrà?")


class NaiveSentenceSimilarityWebservice(object):

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def similarity_ws(self):
        data = cherrypy.request.json
        # print(data)
        # print(type(data))

        j = json.loads(data)

        sentence = j['text']

        result = find_most_similar_sentence(sentence)

        return {'similarity_ws': result}


conf = {
    'similarity_ws': {
    }
}


def web_service_process():
    cherrypy.config.update({'server.socket_port': 8101})
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(NaiveSentenceSimilarityWebservice(), '/', conf)

#
# def web_service_client(host='localhost'):
#     # sample client
#
#     import json
#     import requests
#
#     url = f'http://{host}:8101/similarity_ws'
#
#     my_dict = {'text': 'Cosa posso fare per avere più informazioni?'}
#
#     json_data = json.dumps(my_dict)
#
#     # data = {'json': json_data}
#
#     # https://2.python-requests.org//en/latest/user/quickstart/#post-a-multipart-encoded-file
#     r = requests.post(url, json=json_data)
#
#     print(f"JSON results from web service: {r.text}")
#
#     pass


# if __name__ == '__main__':
#     p = Process(target=web_service_process, args=())
#     p.start()
#
#     web_service_client()
#
#     p.join()


web_service_process()
