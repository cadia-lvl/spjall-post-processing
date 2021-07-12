#!/usr/bin/python3
# Author: Judy Y. Fong lvl@judyyfong.xyz

"""
"""
import json
import requests
from extract import Extraction


def submit_audios(urls, tokens):
    """
        Submit conversation audio files to talgreinir api
        NOTE! This is not used anymore since malla's uploading file works
    """
    api_token = tokens['API_TOKEN']

    tiro_headers = {'Authorization': 'Bearer {}'.format(api_token)}
    new_sessions = get_spjall_audio_files(urls, tokens)
    count = 0
    with open('files_submitted.log', 'a') as files_submitted:
        for client in new_sessions:
            if count >= 2:
                print('{} audio files have been submitted'.format(count),
                      file=files_submitted)
                print('{} audio files have been submitted'.format(count))
                break

            count = count + 1
            tiro_body = {
                'metadata': {
                    'fileType': 'AUDIO',
                    'languageCode': 'is-IS',
                    'subject': client['audio'],
                    'description': '',
                    'keywords': [
                        '__spjallromur__',
                        'TODO',
                        'Máltækniáætlun'
                        ]
                },
                'useUri': True,
                'uri': urls['samromur_url'] + '/' + client['session_id'] +
                       '/' + client['audio']
            }
            tiro_response = requests.post(urls['tiro_url'],
                                          headers=tiro_headers,
                                          data=json.dumps(tiro_body))
            print(tiro_response.json(), file=files_submitted)


def get_subjects_from_transcripts(transcripts):
    """
        Get the subjects from the transcripts

        Only get subjects where the recordingDuration is a number
    """
    submitted_session_ids = []
    for transcript in transcripts:
        if transcript['metadata']['recordingDuration'] is not None:
            if 'storage/' in transcript['metadata']['subject']:
                subject = transcript['metadata']['subject'] \
                    .replace('storage/', '')
            else:
                subject = transcript['metadata']['subject']
            submitted_session_ids.append(subject)
    return submitted_session_ids


def get_spjall_audio_files(urls, transcripts):
    """
        Get the list of all the spjall conversations and corresponding audio
        files
        Return a list of all untranscribed audio files which are over the
        min_duration (60 seconds long). Tiro cannot transcribe audio files
        which are shorter than 1 min long.
    """
    spjall_response = requests.get(urls['spjall_url'])
    new_audio_files = []
    submitted_session_ids = get_subjects_from_transcripts(transcripts)
    min_duration = 60
    for session in spjall_response.json():
        if session is not None:
            client_a_audio = session['session_id'] + '_client_a.wav'
            client_b_audio = session['session_id'] + '_client_b.wav'
            if (client_a_audio not in submitted_session_ids and
                session['client_a']['duration_seconds'] > min_duration):
                client_a = {
                    'session_id': session['session_id'],
                    'audio': client_a_audio
                }
                new_audio_files.append(client_a)
            if (client_b_audio not in submitted_session_ids and
                session['client_b']['duration_seconds'] > min_duration):
                client_b = {
                    'session_id': session['session_id'],
                    'audio': client_b_audio
                }
                new_audio_files.append(client_b)
    return new_audio_files


if __name__ == '__main__':
    FILE_TOKEN = open('config/token.json')
    TOKEN = json.load(FILE_TOKEN)
    URLS_FILE = open('config/urls.json')
    LOCAL_URLS = json.load(URLS_FILE)
    TRANSCRIPTS_OBJECTS = Extraction(LOCAL_URLS, TOKEN)
    TRANSCRIPTS = TRANSCRIPTS_OBJECTS.transcripts

    print("TODO Recordings count: {}".format(TRANSCRIPTS_OBJECTS.get_todo()))

    untranscribed_audio = get_spjall_audio_files(LOCAL_URLS, TRANSCRIPTS)
    print('# of new audio files: {}'.format(len(untranscribed_audio)))

    # submit_audios(LOCAL_URLS, TOKEN)

