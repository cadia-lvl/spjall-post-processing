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
  '''checks if the audio file is already on tiro. Creates body for the files and posts them to tiro.'''
  is_a = False
  is_b = False
  for elem in extracted:
    if elem['metadata']['subject'][0:36] == response.json()[1]['session_id']:
      if elem['metadata']['subject'][44] == "a":
        is_a = True
      elif elem['metadata']['subject'][44] == "b":
        is_b = True
    if is_a and is_b:
      return None

  authorization = {'Authorization' : "Bearer {}".format(API_TOKEN)}

  if not is_a:
    test_a = samromur_url + "/" + response.json()[1]['session_id']+"/"+response.json()[1]['client_a']['session_id']+'/_client_a.wav'
    subject_a = response.json()[1]['session_id']+'_client_a.wav'
    body_a = create_body(subject_a,test_a)
    a_res = requests.post(urls['tiro_url'],data=json.dumps(body_a),headers=authorization)
    print(a_res)

  if not is_b:
    test_b = samromur_url + "/" + response.json()[1]['session_id']+"/"+response.json()[1]['client_b']['session_id']+'/_client_b.wav'
    subject_b = response.json()[1]['session_id']+'_client_b.wav'
    body_b = create_body(subject_b,test_b)
    b_res =requests.post(urls['tiro_url'],data=json.dumps(body_b),headers=authorization)
    print(b_res)

  return None

post(extracted,response)


def create_body(subject,test):
  '''helperfunction that creates the body for the files'''
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