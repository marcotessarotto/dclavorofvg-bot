import cherrypy
import json

from src.ml.nss_utils import find_most_similar_sentence
from src.telegram_bot.ormlayer import orm_get_system_parameter


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

        param = orm_get_system_parameter("DROP_STOP_WORDS")
        remove_stop_words_arg = True if param == "True" else False

        result = find_most_similar_sentence(sentence, remove_stop_words_arg=False)

        # print(result)

        return {'similarity_ws': result}


conf = {
    'similarity_ws': {
    }
}


def web_service_process():
    cherrypy.config.update({'server.socket_port': 8101})
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.quickstart(NaiveSentenceSimilarityWebservice(), '/', conf)


web_service_process()
