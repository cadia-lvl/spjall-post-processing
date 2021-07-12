# Author: Málfríður Anna Eiríksdóttir
# Add to crontab
# 0 16 * * * python3 uploading.py

import json
import requests
from requests.api import head
from extract import Extraction


def post(extracted,spjall_response):
    '''
    Checks if the audio file is already on tiro. Creates body for the files and
    posts them to tiro.

    Some recordings on spjall have audio that's too short, exclude those when
    submitting to Tiro's editor because Tiro always shows them as
    recordingDuration null even if it's actually 2 seconds long.
    '''
    print('Posting files to tiro')
    submitted_file = open('files_submitted_to_tiro.log','w')
    spjall_convo_list = spjall_response.json()
    min_duration = 60
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

        if (not is_a and convo['client_a']['duration_seconds'] > min_duration):
          test_a = samromur_url + "/" + convo['session_id'] + "/"+convo['session_id'] + '_client_a.wav'
          subject_a = convo['session_id']+'_client_a.wav'
          body_a = create_body(subject_a,test_a)
          a_res = requests.post(urls['tiro_url'],data=json.dumps(body_a),headers=authorization)
          print(a_res.json(), file = submitted_file) 

        if (not is_b and convo['client_b']['duration_seconds'] > min_duration):
          test_b = samromur_url + "/" + convo['session_id'] + "/"+convo['session_id'] + '_client_b.wav'
          subject_b = convo['session_id']+'_client_b.wav'
          body_b = create_body(subject_b,test_b)
          b_res = requests.post(urls['tiro_url'],data=json.dumps(body_b),headers=authorization)
          print(b_res.json(),file = submitted_file) 

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
    urls_file = open('config/urls.json')
    urls = json.load(urls_file)

    token_file = open('config/token.json')
    tokens = json.load(token_file)

    API_TOKEN = tokens['API_TOKEN']

    spjall_response = requests.get(urls['spjall_url'])

    samromur_url = urls['samromur_url']

    transcripts_objects = Extraction(urls,tokens)
    extracted = transcripts_objects.filter_transcripts('__spjallromur__')
    
    post(extracted,spjall_response)