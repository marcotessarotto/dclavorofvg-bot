

# pip install requests


import json
import requests

url = 'http://localhost:8080/my_endpoint'

files = {'file': open('/home/marco/test.txt', 'rb'), 'file2': open('/home/marco/test.txt', 'rb'),}
my_dict = {'some': 'data'}
json_data = json.dumps(my_dict)

data = {'json': json_data}




# https://2.python-requests.org//en/latest/user/quickstart/#post-a-multipart-encoded-file
r = requests.post(url, files=files, json=json_data, data=data)

print(r.text)



if False:

    import base64

    with open("yourfile.ext", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())


    #https://stackoverflow.com/questions/24642040/using-python-requests-to-send-file-and-json-in-single-request

    url = 'my-url.com/api/endpoint'
    headers = {'Authorization': 'my-api-key'}
    image_metadata = {'key1': 'value1', 'key2': 'value2'}
    data = {'name': 'image.jpg', 'data': json.dumps(image_metadata)}
    files = {'file': (FILE, open(PATH, 'rb'), 'image/jpg', {'Expires': '0'})}
    r = requests.post(url, files=files, headers=headers, data=data)