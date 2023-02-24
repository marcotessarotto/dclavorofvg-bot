import io
import json
import os

import cherrypy
from cherrypy._cpreqbody import Part


class VacanciesWebservice(object):

    # https://docs.cherrypy.org/en/latest/_modules/cherrypy/tutorial/tut09_files.html#FileDemo.upload

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def my_endpoint(self, *args, **kwargs):
        print("my_endpoint")

        print(args)
        print(kwargs)

        for k in kwargs:
            print("param name: ")
            print(k)

            print("param obj: ")
            data = kwargs[k]
            print(data)

            if isinstance(data, Part):
                print("this is a file!")

                content = data.file.read()
                print("content len = " + str(len(content)))

                path = '/tmp/vac.txt'
                fp = open(path, mode='wb')
                fp.write(content)
                fp.close()

                stat = os.stat(path)
                print(stat)


                with open(path) as fd:
                    json_data = json.load(fd)

                    print(json.dumps(json_data, indent=4))

                    for item in json_data:
                        print(type(item))

                        for k, v in item.items():
                            print(k, v)
                            print(type(v))

                        print(item['vacancyExtendedInfo']['categoriaProfessionale'])

                        break



                pass

        result = {"operation": "request", "result": "success"}

        print("my_endpoint - finished")

        return result


conf = {
    'my_endpoint': {

    }
}

# https://docs.cherrypy.org/en/latest/_modules/cherrypy/lib/auth_digest.html
# tools.auth_digest.key is a secret key used by server for calculating nonces

# https://stackoverflow.com/questions/46441679/enabling-digest-authentication-in-cherrypy-server-conf#46454409


# https://stackoverflow.com/questions/3743769/how-to-receive-json-in-a-post-request-in-cherrypy#18367567

from multiprocessing import Process


def web_service_process():
    cherrypy.config.update({'server.socket_port': 8099})
    # cherrypy.config.update({'server.host': 'localhost'})
    cherrypy.quickstart(VacanciesWebservice(), '/', conf)


def web_service_client():
    # sample client

    import json
    import requests

    url = 'http://localhost:8099/my_endpoint'

    files = {'file': open('/home/marco/vacancies.txt', 'rb'),  }
    my_dict = {'some': 'data'}
    json_data = json.dumps(my_dict)

    data = {'json': json_data}

    # https://2.python-requests.org//en/latest/user/quickstart/#post-a-multipart-encoded-file
    r = requests.post(url, files=files, json=json_data, data=data)

    print(r.text)

    pass


if __name__ == '__main__':
    p = Process(target=web_service_process, args=())
    p.start()

    web_service_client()

    p.join()




