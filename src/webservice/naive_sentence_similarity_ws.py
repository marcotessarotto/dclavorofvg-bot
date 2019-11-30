import cherrypy
import json

from multiprocessing import Process

from src.telegram_bot.nss_utils import find_most_similar_sentence


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
