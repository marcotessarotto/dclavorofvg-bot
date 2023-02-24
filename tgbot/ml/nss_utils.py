# naive_sentence_similarity
from tgbot.telegram_bot.log_utils import benchmark_decorator

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

# from tgbot.telegram_bot.log_utils import ws_logger as logger, log_user_input, debug_update

# from tgbot.backoffice.models import *

from tgbot.telegram_bot.ormlayer import orm_get_nss_reference_sentences, orm_get_obj_from_cache, orm_set_obj_in_cache

# useful materials:
# https://nlpforhackers.io/wordnet-sentence-similarity/
# https://www.aaai.org/Papers/AAAI/2006/AAAI06-123.pdf
# https://github.com/sujitpal/nltk-examples/blob/master/src/semantic/short_sentence_similarity.py
# https://nlpforhackers.io/wordnet-sentence-similarity/
# https://stackoverflow.com/questions/16877517/compare-similarity-of-terms-expressions-using-nltk
# https://sites.temple.edu/tudsc/2017/03/30/measuring-similarity-between-texts-in-python/
# https://stackoverflow.com/questions/46732843/compare-two-sentences-on-basis-of-grammar-using-nlp


# treetagger configuration
tagbuildopt = {"TAGDIR": '/opt/bot/treetagger', "TAGLANG": "it"}
tagger = TreeTagger(**tagbuildopt)


_stoplist = set(stopwords.words('italian'))

keep_words = {"non", "dove", "quanto", "quando"}
for w in keep_words:
    if w in _stoplist:
        _stoplist.remove(w)

# print(_stoplist)


def remove_stop_words(text, print_log=False):
    tokenized_sent = word_tokenize(text.lower())
    tokenized_sent_nostop = [token for token in tokenized_sent if token not in _stoplist]
    result = " ".join(tokenized_sent_nostop)
    if print_log:
        print(f"remove_stop_words:\n***BEFORE: {text}\n***AFTER : {result}")
    return result


process_sentence_cache_dict = {}


def process_sentence(sentence, remove_stop_words_arg=True, remove_punctuation=True, print_log=False, return_all_results=False):

    key_name = "nss_sentence_" + sentence + "-rsw" if remove_stop_words_arg else ""
    res = process_sentence_cache_dict.get(key_name)
    if res:
        return res

    if print_log:
        print(f"process_sentence sentence='{sentence}'")

    # if remove_stop_words_arg:
    #     sentence = remove_stop_words(sentence, print_log=print_log)

    dict = {}

    tagger_result = tagger.tag_text(sentence)
    result = []

    for s in tagger_result:
        w = s.split('\t')

        if len(w) <= 1:
            continue

        if remove_punctuation and w[1] == 'PON':
            continue

        if remove_stop_words_arg and w[2] in _stoplist:
            continue

        w.append(None)

        result.append(w)

    if print_log:
        print(f"tagger_result: {result}")

    for row in result:
        word = row[2]
        # print(f"analysis of word '{word}'")

        # http://www.nltk.org/howto/wordnet.html
        synsets = wn.synsets(word, lang="ita")

        dict[word] = synsets

    # mark_entities(result)

    if print_log:
        print(f"process_sentence result  sentence='{sentence}'")
        for k,v in dict.items():
            print(f"'{k}' = '{v}'")

    if not return_all_results:
        result = None

    process_sentence_cache_dict[key_name] = (dict, result)

    return dict, result


def calc_dict_average(d):

    if len(d) == 0:
        return 0

    res = 0
    for k1, v1 in d.items():
        if v1:
            res += v1

    res = res / len(d)

    return res


similarity_cache = {}


def compare_sentences(d1, d2, lch_similarity=False, print_log=False, use_keys_for_matching=True):

    dict = {}

    # first, compare by key values
    if use_keys_for_matching:
        for k1 in d1:
            for k2 in d2:
                if k1 == k2:
                    # print(f"MATCH on KEY! {k1} ")
                    dict[k1] = 1
                    break

    # secondly, compare by values
    for k1, v1 in d1.items():  # v1 is a list

        max_similarity = 0
        # best_match = None
        max_pos = 0

        if k1 in dict:
            continue

        for synset1 in v1:

            for k2, v2 in d2.items():

                pos = 0

                for synset2 in v2:

                    cache_key = synset1._name + "**" + synset2._name

                    similarity = similarity_cache.get(cache_key)

                    if similarity is None:

                        if lch_similarity:
                            similarity = synset1.lch_similarity(synset2)
                        else:
                            similarity = synset1.path_similarity(synset2)  # can return None

                        if similarity is None:
                            similarity_cache[cache_key] = -1
                        else:
                            similarity_cache[cache_key] = similarity

                        # print(f"stored cache_key={cache_key}")

                    else:
                        if similarity == -1:
                            similarity = None
                        # print(f"cache_key={cache_key} is *CACHED*")

                    # print(f"similarity={similarity}  synset1={synset1} synset2={synset2}")

                    if similarity and similarity > max_similarity:
                        max_similarity = similarity
                        # best_match = synset2
                        max_pos = pos

                    pos = pos + 1

        calc_max_similarity = max_similarity
        if max_pos > 0:
            calc_max_similarity = calc_max_similarity / max_pos

        # print(f"max similarity between '{k1}' and sentence: max={maxval}, calc_maxval={calc_maxval}, best_match={best_match}, maxpos={maxpos}")

        dict[k1] = calc_max_similarity

    return calc_dict_average(dict), dict


@benchmark_decorator
def find_most_similar_sentence(sentence, method_for_reference_sentences=orm_get_nss_reference_sentences, print_log=False, remove_stop_words_arg=True, return_all_results=False):
    """returns (result, confidence, ordered dictionary of most similar sentences) """

    confidence = 0
    result = None
    confidence_sentence = None
    tree_tagger_best_match = None

    d2, tr2 = process_sentence(sentence, print_log=print_log, remove_stop_words_arg=remove_stop_words_arg, return_all_results=return_all_results)

    rdict = {}

    reference_sentences = method_for_reference_sentences()

    for item in reference_sentences:

        try:
            ref_sentence = item.reference_sentence
            ref_target = item.action.action if item.action is not None else ""
            ref_context = item.context.context if item.context is not None else ""
        except AttributeError:
            print(f"***error! {item}")
            ref_sentence = item[0]
            ref_target = item[1]

        if ref_sentence is None or len(ref_sentence) == 0:
            continue

        d1, tr1 = process_sentence(ref_sentence, print_log=print_log, remove_stop_words_arg=remove_stop_words_arg, return_all_results=return_all_results)

        r1 = compare_sentences(d1, d2)
        r2 = compare_sentences(d2, d1)

        val = (r1[0] + r2[0]) / 2.

        rdict[val] = (ref_sentence, ref_target, ref_context)

        if val > confidence:
            confidence = val
            result = ref_target
            confidence_sentence = ref_sentence
            tree_tagger_best_match = tr1

    # print(rdict)

    sorted_dict = {i: rdict[i] for i in sorted(rdict.keys(), reverse=True)}  # sort dict by key value in reverse order

    # print(sorted_dict)

    if len(sorted_dict) > 0:
        first_key = next(iter(sorted_dict))
        first_val = sorted_dict[first_key]

        # print(first_key)
        # print(first_val)
        confidence = first_key
        result = first_val[1]

        # mismatch between (result, confidence) and first item of sorted_dict
        # issue:  'dove stanno le notizie?' => {'similarity_ws': ['SHOW_PARTICULAR_NEWS_ITEM', 0.7589285714285714, {'0.7589285714285714': ['dove trovo le notizie?', 'SHOW_LAST_NEWS'], '0.6857638888888888': .....

    print(f"find_most_similar_sentence(): confidence={confidence} | result={result} | sentence='{sentence}' | confidence_sentence='{confidence_sentence}' | remove_stop_words_arg='{remove_stop_words_arg}'")

    return result, confidence, sorted_dict, tr2, tree_tagger_best_match


def test_nss():
    find_most_similar_sentence("dove mi trovo?")

    find_most_similar_sentence("maggiori info")

    find_most_similar_sentence("maggiori informazioni")

    find_most_similar_sentence("a chi posso chiedere?")

    find_most_similar_sentence("a chi posso telefonare?")

    find_most_similar_sentence("a chi posso mandare una email?")

    find_most_similar_sentence("a chi posso chiedere chiarimenti su dove si terrà?")
