# Author: Málfríður Anna Eiríksdóttir

import json
import requests
from requests.api import head
from extract import Extraction


def post(extracted,spjall_response):
    '''checks if the audio file is already on tiro. Creates body for the files and posts them to tiro.'''
    print('Posting files to tiro')
    submitted_file = open('files_submitted_to_tiro.log','w')
    counter = 0
    spjall_convo_list = spjall_response.json()
    for convo in spjall_convo_list:
      is_a = False
      is_b = False
      if convo != None:
        for elem in extracted:
          if elem['metadata']['recordingDuration'] != None:
            if convo['session_id'] in elem['metadata']['subject']:
              if 'client_a' in elem['metadata']['subject']:
                is_a = True
              elif 'client_b' in elem['metadata']['subject']:
                is_b = True
     

        authorization = {'Authorization': "Bearer {}".format(API_TOKEN)}

        if not is_a:
          test_a = samromur_url + "/" + convo['session_id'] + "/"+convo['session_id'] + '_client_a.wav'
          subject_a = convo['session_id']+'_client_a.wav'
          body_a = create_body(subject_a,test_a)
          a_res = requests.post(urls['tiro_url'],data=json.dumps(body_a),headers=authorization)
          counter += 1
          print(a_res.json(), file = submitted_file) 
          if counter>=10:
            return

        if not is_b:
          test_b = samromur_url + "/" + convo['session_id'] + "/"+convo['session_id'] + '_client_b.wav'
          subject_b = convo['session_id']+'_client_b.wav'
          body_b = create_body(subject_b,test_b)
          b_res = requests.post(urls['tiro_url'],data=json.dumps(body_b),headers=authorization)
          counter += 1
          print(b_res.json(),file = submitted_file) 
          if counter>=10:
            print('10 files have been sumbitted')
            return

    if counter == 0:
      print('No files need to be submitted.')

    if 0 < counter < 10:
      print('All non-transcribed convos have been submitted to tiro')
    return None


def create_body(subject,test):
    '''helper function that creates the body for the tiro/talgreinir submit post request'''
    body = {
      "metadata": {
        "fileType": "AUDIO",
        "languageCode": "is-IS",
        "subject": subject,
        "description": "",
        "keywords": [
          "__spjallromur__",
          "M\u00e1lt\u00e6kni\u00e1\u00e6tlun",
          "TODO"
        ]
      },
      "useUri": True,
      "uri": test
    }
    return body

if __name__ == "__main__":
    urls_file = open('urls.json')
    urls = json.load(urls_file)

    token_file = open('token.json')
    tokens = json.load(token_file)

    API_TOKEN = tokens['API_TOKEN']

    spjall_response = requests.get(urls['spjall_url'])

    samromur_url = urls['samromur_url']

    transcripts_objects = Extraction(urls,tokens)
    extracted = transcripts_objects.filter_transcripts('__spjallromur__')
    
    post(extracted,spjall_response)