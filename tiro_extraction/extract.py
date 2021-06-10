import requests
import json
import os


class Extraction:
    def __init__(self, urls, token):
        self.headers = {'Authorization' : token['api_token']}
        self.urls = urls
        self.transcripts = self.extract_transcripts()

    def extract_transcripts(self):
        """ Gets the transcripts from the Tiro API """
        response = requests.get(self.urls['transcripts_url'], headers=self.headers)
        transcripts = response.json()['transcripts']

        write_json_to_file(transcripts, "transcripts.json")

        return transcripts

    def filter_transcripts(self, kw):
        """ Filters transcripts by keyword """
        # TODO: From the API, it's a bit funky ?
        # filter = '[%22{}%22]'.format(tag)
        # print(self.urls['filter_transcripts_url'] + filter)
        # response = requests.get(self.urls['filter_transcripts_url']+filter, headers=self.headers)
        # transcripts = response.json() 

        
        # Not using the API filter, but it functions for now.
        filtered = [obj for obj in self.transcripts if (kw in obj['metadata']['keywords'])]
        # write_json_to_file(filtered, "filtered.json")    

        return filtered

    def get_progress(self):
        """ Returns the % of transcribed conversation """
        transcribed = self.filter_transcripts("TRANSCRIBED")
        print(len(transcribed) / len(self.transcripts) * 100)
        return len(transcribed) / len(self.transcripts) * 100


def load_json(json_file):
    """ Loads data from a JSON file """
    json_obj = open(json_file)
    data = json.load(json_obj)
    json_obj.close()

    return data

def write_json_to_file(json_object, filename):
    """ Writes a JSON object to a file, mostly for testing as it is """
    with open("json_files/" + filename, 'w') as outfile:
        json.dump(json_object, outfile, indent=4)


if __name__ == '__main__':
    os.chdir("tiro_extraction/")

    urls = load_json('json_files/urls.json')
    token = load_json('json_files/token.json')

    extract = Extraction(urls, token)
    extract.get_progress()

