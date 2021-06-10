


import json
import requests
f = open('urls.json')
urls = json.load(f)

token = open('token.json')
t = json.load(token)

API_TOKEN = t['API_TOKEN']


headers={'Authorization' : API_TOKEN}

response = requests.get(urls['spjall_url'], headers=headers)

# print(response.json())
saromur_url = urls['samromur_urls']

for elem in response.json():
    if elem != None:
        print(saromur_url+"/"+elem['session_id']+"/"+elem['client_a']['session_id']+'/_client_a.wav')
        res = requests.get(saromur_url+"/"+elem['session_id']+"/"+elem['client_a']['session_id']+'/_client_a.wav', headers=headers)

        print(res)

        #print(elem['client_a']['session_id'])
        print('\n')


test = urls['test_audio']
