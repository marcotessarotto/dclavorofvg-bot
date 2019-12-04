# naive_sentence_similarity
from src.telegram_bot.log_utils import benchmark_decorator

print(__file__)

import time
from functools import wraps

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize


# install treetagger from here:
# https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/
# italian tagset:
# https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/italian-tagset.txt

from treetaggerwrapper import TreeTagger

# from src.telegram_bot.log_utils import ws_logger as logger, log_user_input, debug_update

# from src.backoffice.models import *

from src.telegram_bot.ormlayer import orm_get_nss_reference_sentences, orm_get_obj_from_cache, orm_set_obj_in_cache


tagbuildopt = {"TAGDIR": '/opt/bot/treetagger', "TAGLANG": "it"}
tagger = TreeTagger(**tagbuildopt)


_stoplist = set(stopwords.words('italian'))


def remove_stop_words(text):
    tokenized_sent = word_tokenize(text.lower())
    tokenized_sent_nostop = [token for token in tokenized_sent if token not in _stoplist]
    result = " ".join(tokenized_sent_nostop)
    # print(f"remove_stop_words:\n***BEFORE: {text}\n***AFTER : {result}")
    return result


process_sentence_cache_dict = {}


def process_sentence(sentence, remove_stop_words_arg=True, remove_punctuation=True):

    key_name = "nss_sentence_" + sentence
    res = process_sentence_cache_dict.get(key_name)
    if res:
        return res

    if remove_stop_words_arg:
        sentence = remove_stop_words(sentence)

    dict = {}

    tagger_result = tagger.tag_text(sentence)
    result = []

    for s in tagger_result:
        w = s.split('\t')

        if len(w) <= 1:
            continue

        if remove_punctuation and w[1] == 'PON':
            continue

        result.append(w)

    for row in result:
        word = row[2]
        # print(f"analysis of word '{word}'")

        # http://www.nltk.org/howto/wordnet.html
        synsets = wn.synsets(word, lang="ita")

        dict[word] = synsets

    process_sentence_cache_dict[key_name] = dict

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


@benchmark_decorator
def find_most_similar_sentence(sentence, method_for_reference_sentences=orm_get_nss_reference_sentences):
    """returns (result, confidence, ordered dictionary of most similar sentences) """

    confidence = 0
    result = None
    confidence_sentence = None

    d2 = process_sentence(sentence)

    rdict = {}

    reference_sentences = method_for_reference_sentences()

    for item in reference_sentences:

        try:
            ref_sentence = item.reference_sentence
            ref_target = item.action.action if item.action is not None else ""
        except AttributeError:
            print(f"***error! {item}")
            ref_sentence = item[0]
            ref_target = item[1]

        if ref_sentence is None or len(ref_sentence) == 0:
            continue

        d1 = process_sentence(ref_sentence)

        r1 = compare_sentences(d1, d2)
        r2 = compare_sentences(d2, d1)

        val = (r1[0] + r2[0]) / 2.

        rdict[val] = (ref_sentence, ref_target)

        if val > confidence:
            confidence = val
            result = ref_target
            confidence_sentence = ref_sentence

    # print(rdict)

    sorted_dict = {i: rdict[i] for i in sorted(rdict.keys(), reverse=True)}  # sort dict by key value in reverse order

    # print(sorted_dict)

    if len(sorted_dict) > 0:
        first_key = next(iter(sorted_dict))
        first_val = sorted_dict[first_key]

        print(first_key)
        print(first_val)
        confidence = first_key
        result = first_val[1]


        # mismatch between (result, confidence) and first item of sorted_dict
        # issue:  'dove stanno le notizie?' => {'similarity_ws': ['SHOW_PARTICULAR_NEWS_ITEM', 0.7589285714285714, {'0.7589285714285714': ['dove trovo le notizie?', 'SHOW_LAST_NEWS'], '0.6857638888888888': .....

    print(f"find_most_similar_sentence(): confidence={confidence} | result={result} | sentence='{sentence}' | confidence_sentence='{confidence_sentence}'")

    return result, confidence, sorted_dict


 # reference_sentence = "Come posso fare per avere più informazioni?"

# reference_sentences = [
#     ("come posso fare per avere più informazioni?", "MORE_INFO"),
#     ("a chi posso chiedere informazioni?", "MORE_INFO_WHO"),
#     ("dove posso chiedere informazioni?", "MORE_INFO_WHERE"),
#     ("come mi iscrivo?", "HOW_TO_ENROLL"),
#     ("quando si tiene l'evento?", "WHEN_IS_EVENT"),
#     ("quando ci sarà l'evento?", "WHEN_IS_EVENT"),
#     ("quando si tiene il corso?", "WHEN_IS_COURSE"),
#     ("quando ci sarà il corso?", "WHEN_IS_COURSE"),
#     ("chi tiene il corso?","WHO_IS_COURSE_ORGANIZER"),
#     ("chi organizza il corso?","WHO_IS_COURSE_ORGANIZER"),
#     ("mi sono perso","HELP"),
#     ("non capisco","HELP"),
#     ("maggiori informazioni","MORE_INFO_GENERAL"),
#     ("chi posso contattare","MORE_INFO_CONTACT"),
#     ("ho bisogno di una mano","HELP"),
#     ("non capisco","HELP"),
#     ("esiste un tutorial","HELP_TUTORIAL"),
#     ("aiuto con i comandi del bot","HELP_BOT_COMMANDS"),
#     ("come scelgo le categorie?","HELP_CHOOSE_NEWS_CATEGORIES"),
#     ("voglio più informazioni sui comandi","HELP_BOT_COMMANDS"),
#     ("dove sono le offerte di lavoro?","HELP_JOB_OFFERS"),
#     ("in che linguaggio è scritto il bot","HELP_BOT_DEV"),
#     ("info comandi bot","HELP_BOT_COMMANDS"),
#     ("", ""),
#     ("", ""),
# ]


def test_nss():
    find_most_similar_sentence("dove mi trovo?")

    find_most_similar_sentence("maggiori info")

    find_most_similar_sentence("maggiori informazioni")

    find_most_similar_sentence("a chi posso chiedere?")

    find_most_similar_sentence("a chi posso telefonare?")

    find_most_similar_sentence("a chi posso mandare una email?")

    find_most_similar_sentence("a chi posso chiedere chiarimenti su dove si terrà?")
