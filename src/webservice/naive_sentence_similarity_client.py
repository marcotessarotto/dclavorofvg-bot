import json
import requests


def naive_sentence_similarity_web_client(sentence, host='localhost'):

    url = f'http://{host}:8101/similarity_ws'

    my_dict = {'text': sentence}

    json_data = json.dumps(my_dict)

    r = requests.post(url, json=json_data)

    # print(f"naive_sentence_similarity_web_client: result={r.text} sentence='{sentence}'")

    return r.text


# sentence = 'chi organizza il corso'
#
# j = naive_sentence_similarity_web_client(sentence)
#
# print(j)
#
#
# import json
#
# d = json.loads(j)
#
# print(d['similarity_ws'])
#

