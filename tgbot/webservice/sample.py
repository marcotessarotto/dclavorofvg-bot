import cherrypy

# pip install cherrypy


class Root:

# https://docs.cherrypy.org/en/latest/_modules/cherrypy/tutorial/tut09_files.html#FileDemo.upload

    @cherrypy.expose
    @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    def my_endpoint(self, *args, **kwargs):

        print("ok received!")

        print(args)
        print(kwargs)

        for k in kwargs:
            print(k)
            print(kwargs[k])
            # print(v)

        # input_json = cherrypy.request.json
        # print(input_json)

        result = {"operation": "request", "result": "success"}

        return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def my_route(self):
        print("ok!")

        result = {"operation": "request", "result": "success"}

        input_json = cherrypy.request.json
        value = input_json["my_key"]

        # Responses are serialized to JSON (because of the json_out decorator)
        return result

    @cherrypy.expose
    def index(self):
        return """
<html>
<script type="text/javascript" tgbot="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
<script type='text/javascript'>

function Update() {

    var myObject = { "my_key": "my_value" };

    $.ajax({
        type: "POST",
        url: "my_route",
        data: JSON.stringify(myObject),
        contentType: 'application/json',
        dataType: 'json',
        error: function() {
            alert("error");
        },
        success: function() {
            alert("success");
        }
    });

}
</script>
<body>
<input type='textbox' id='updatebox' value='{}' size='20' />
<input type='submit' value='Update' onClick='Update(); return false' />
</body>
</html>
"""

# https://docs.cherrypy.org/en/latest/basics.html#id31

from cherrypy.lib import auth_digest

USERS = {'jon': 'secret'}

conf = {
    '/my_route': {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
        'tools.auth_digest.key': 'a565c27146791cfb',
        'tools.auth_digest.accept_charset': 'UTF-8',
   }
}

# https://docs.cherrypy.org/en/latest/_modules/cherrypy/lib/auth_digest.html
# tools.auth_digest.key is a secret key used by server for calculating nonces

# https://stackoverflow.com/questions/46441679/enabling-digest-authentication-in-cherrypy-server-conf#46454409


# https://stackoverflow.com/questions/3743769/how-to-receive-json-in-a-post-request-in-cherrypy#18367567

cherrypy.quickstart(Root(), '/', conf)
