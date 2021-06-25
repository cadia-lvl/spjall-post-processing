import json
import requests
from requests.api import head

urls_file = open('urls.json')
urls = json.load(urls_file)

token_file = open('token.json')
tokens = json.load(token_file)

extracted_file = open('transcripts.json')
extracted = json.load(extracted_file)


API_TOKEN = tokens['API_TOKEN']


response = requests.get(urls['spjall_url'])

samromur_url = urls['samromur_url']

def post(extracted,response):
  for elem in extracted:
    if elem['metadata']['subject'][0:36] == response.json()[1]['session_id']:
      return None
  test_a = samromur_url + "/" + response.json()[1]['session_id']+"/"+response.json()[1]['client_a']['session_id']+'/_client_a.wav'
  test_b = samromur_url + "/" + response.json()[1]['session_id']+"/"+response.json()[1]['client_b']['session_id']+'/_client_b.wav'
  subject_a = response.json()[1]['session_id']+'_client_a.wav'
  subject_b = response.json()[1]['session_id']+'_client_b.wav'

  body_a = create_body(subject_a,test_a)


  authorization = {'Authorization' : "Bearer {}".format(API_TOKEN)}
  a_res = requests.post(urls['tiro_url'],data=json.dumps(body_a),headers=authorization)
  print(a_res)

  body_b = create_body(subject_b,test_b)


  authorization = {'Authorization' : "Bearer {}".format(API_TOKEN)}


  b_res =requests.post(urls['tiro_url'],data=json.dumps(body_b),headers=authorization)
  print(b_res)

  return None


post(extracted,response)

def create_body(subject,test):
  body = {
  "metadata": {
    "fileType": "AUDIO",
    "languageCode": "is-IS",
    "subject": subject,
    "description": "",
    "keywords": [
      "this is a test",
      #"__spjallromur__",
      #"M\u00e1lt\u00e6kni\u00e1\u00e6tlun",
      #"TODO"
      
    ]
  },
  "useUri": True,
  "uri": test
  
  }
  return body


print('test')
# /usr/local/bin/python3 /Users/malla/Documents/spjall-post-processing/extract.py /Users/malla/Documents/spjall-post-processing/urls.json /Users/malla/Documents/spjall-post-processing/token.json