import cherrypy
import json

from treetaggerwrapper import TreeTagger

from multiprocessing import Process

"""
simple web service which embeds treetagger
"""

# install treetagger from here:
# https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/


tagbuildopt = {}
tagbuildopt["TAGDIR"] = '/opt/bot/treetagger'  # location on fs where treetagger is installed (follow instructions on website)
tagbuildopt["TAGLANG"] = "it"

tagger = TreeTagger(**tagbuildopt)


class TreetaggerWebservice(object):

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def treetagger_ws(self):
        data = cherrypy.request.json
        # print(data)
        # print(type(data))

        j = json.loads(data)

        sentence = j['text']

        result = []

        tagger_result = tagger.tag_text(sentence)

        # https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/italian-tagset.txt
        for s in tagger_result:

            w = s.split('\t')

            result.append(w)

        return {'treetagger_result': result}

conf = {
    'treetagger_ws': {
    }
}


def web_service_process():
    cherrypy.config.update({'server.socket_port': 8100})
    cherrypy.config.update({'server.host': '0.0.0.0'})
    cherrypy.quickstart(TreetaggerWebservice(), '/', conf)


def web_service_client():
    # sample client

    import json
    import requests

    url = 'http://localhost:8100/treetagger_ws'

    my_dict = {'text': 'Come posso fare per avere più informazioni?'}

    json_data = json.dumps(my_dict)

    # data = {'json': json_data}

    # https://2.python-requests.org//en/latest/user/quickstart/#post-a-multipart-encoded-file
    r = requests.post(url, json=json_data )

    print(f"JSON results from web service: {r.text}")

    pass


web_service_process()

# if __name__ == '__main__':
#     p = Process(target=web_service_process, args=())
#     p.start()
#
#     web_service_client()
#
#     p.join()