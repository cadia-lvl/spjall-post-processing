import requests
import json
import argparse
import re
import os
import shutil


class Extraction:
    def __init__(self, urls, token):
        self.headers = {'Authorization': 'Bearer ' + token['api_token']}
        self.urls = urls
        self.transcripts = self.extract_transcripts()

    """
    General extraction and filtering
    """

    def extract_transcripts(self):
        """ Gets the transcripts from the Tiro API """
        response = requests.get(self.urls['transcripts_url'], headers=self.headers)

        # If user is not authenticated, or an error occurs.
        if 'message' in response.json():
            print(response.json()['message'])
            # print("Fetching public transcripts...")

            # response = requests.get(self.urls['transcripts_url'])
            # transcripts = response.json()['transcripts']

            # print("Public transcripts extracted.")

            transcripts = response.json()

        else:
            transcripts = response.json()['transcripts']

            # print("Transcripts extracted.")

        # Filter so that only the conversation transcripts are stored
        self.transcripts = transcripts
        transcripts = self.filter_transcripts("__spjallromur__")
        # write_json_to_file(transcripts, "testing/transcripts.json")

        return transcripts

    def filter_transcripts(self, kw):
        """ Filters transcripts by keyword """
        filtered = [obj for obj in self.transcripts if (kw in obj['metadata']['keywords'])]
        # write_json_to_file(filtered, "filtered.json")

        return filtered

    def get_progress(self):
        """ Returns the % of transcribed files """
        transcribed = self.filter_transcripts("TRANSCRIBED")

        return len(transcribed) / len(self.transcripts) * 100

    """
    Transcript oriented processing
    """

    def get_transcript_by_id(self, transcript_id):
        """ Gets a transcript by id """
        response = requests.get(self.urls['transcripts_url'] + '/' + transcript_id, headers=self.headers)
        transcript = response.json()

        # write_json_to_file(transcript, "transcript.json")

        return transcript

    def get_subject_data(self, json_transcript):
        """ Gets subject data (convo and speaker) of a transcript """
        # Split on _ or .
        convo, _, speaker, _ = re.split('_|\.', json_transcript['metadata']['subject'])

        return convo, speaker

    def get_transcript_id(self, transcript):
        """ Gets the id of a transcript """
        _, transcript_id = transcript['name'].split("/")

        return transcript_id

    def get_audio_file_from_uri(self, transcript, filepath):
        """ Downloads the audio file from the uri of a transcript"""
        response = requests.get(transcript['uri'], headers=self.headers)
        with open('{}.wav'.format(filepath), 'wb') as f:
            f.write(response.content)

    def get_metadata(self, convo, speaker):
        """ Gets the JSON metadata of a speaker in a conversation """
        response = requests.get(urls['metadata'] + '/{}/{}_client_{}.json'.format(convo, convo, speaker))
        metadata = response.json()

        # write_json_to_file(metadata, 'metadata.json')

        return metadata

    def write_to_log(self, str, filename):
        """ Writes a message to a log text file """
        with open(filename, 'a+') as f:
            f.seek(0)
            contents = f.read(100)
            # If the file is not empty, add a new line.
            if len(contents) > 0:
                f.write('\n')

            f.write(str)

    def clear_log(self, filename):
        """ Clears the text file  for new logging """
        open(filename, 'w').close()

    def make_conversation_directory(self):
        """ Creates a directory for each conversation, containing corresponding audio and json files. """
        print("Creating directory for each conversation. This might take a moment...")
        log_file = 'dir_log.txt'
        self.clear_log(log_file)

        try:
            os.mkdir("conversations")
        # If conversations directory already exists, clear it.
        except FileExistsError:
            print("Clearing conversations directory...")
            for dir in os.listdir("conversations"):
                shutil.rmtree("conversations/" + dir)

        count = 0
        not_added = 0
        for t in self.transcripts:
            transcript_id = self.get_transcript_id(t)
            # If the transcript is invalid, a test transcript, or unifinished, it will not be added to a directory.
            if t in self.filter_transcripts("INVALID"):
                self.write_to_log("Transcript {} is invalid and was not added to directory.".format(transcript_id), log_file)
                not_added += 1
            # TODO: Remove if guaranteed that no test transcript has __spjallromur__/TRANSCRIBED/PROOFREAD tag, otherwise the subject parsing causes problems.
            elif t['metadata']['subject'] == "Test Spegillinn":
                self.write_to_log("Transcript {} is a test transcript and was not added to directory.".format(transcript_id), log_file)
                not_added += 1
            elif t in self.filter_transcripts("TODO") or t in self.filter_transcripts("INPROGRESS"):
                self.write_to_log("Transcript {} is unfinished and was not added to directory.".format(transcript_id), log_file)
                not_added += 1
            # If the transcript has been marked as transcribed or proofread, add it to a corresponding directory.
            elif t in self.filter_transcripts("TRANSCRIBED") or t in self.filter_transcripts("PROOFREAD"):
                # Get the transcript by id to access the uri for the audio file
                transcript = self.get_transcript_by_id(transcript_id)
                convo, speaker = self.get_subject_data(transcript)
                t_metadata = self.get_metadata(convo, speaker)

                # valid = self.validate_transcript_metadata_duration(t, t_metadata)
                # if not valid:
                #     self.write_to_log("Transcript {} and its metadata (/{}/{}_client_{}.json) duration do not match. Transcript not added to directory.".format(transcript_id, convo, convo, speaker), log_file)
                #     not_added += 1
                #     continue

                # Where the file should be written
                filepath = "conversations/{}/speaker_{}_convo_{}".format(convo, speaker, convo)
                try:
                    os.mkdir("conversations/{}".format(convo))
                    self.get_audio_file_from_uri(transcript, filepath)
                    write_json_to_file(t_metadata, filepath + "_meta.json")
                    write_json_to_file(transcript, filepath + "_transcript.json")
                # If a directory for a conversation exists, just add the corresponding files.
                except FileExistsError:
                    self.get_audio_file_from_uri(transcript, filepath)
                    write_json_to_file(t_metadata, filepath + "_meta.json")
                    write_json_to_file(transcript, filepath + "_transcript.json")
                # If the conversation name contains a file path.
                except FileNotFoundError:
                    self.write_to_log("Could not create directory for {}. Transcript name contains a filepath.".format(convo), log_file)
                    not_added += 1
            else:
                self.write_to_log("Transcript {} has unapproved tags and was not added to directory.".format(transcript_id), log_file)
                not_added += 1

            count += 1
            print("{}/{} transcripts processed.".format(count, len(self.transcripts)))

        if not_added > 0:
            print("{} transcripts were not added to a directory. Refer to dir_log.txt for further information.".format(not_added))
        print("Completed.")

    """
    Transcript validation
    """

    def validate_transcript_duration(self, transcript):
        """ Validates the length of the transcript. Returns False if invalid, True otherwise. """
        audio_duration = float(transcript['metadata']['recordingDuration'][:-1])
        # if the last segment time stamps exceed that of the audio duration
        last_segment = transcript['segments'][-1]
        if float(last_segment['endTime'][:-1]) > audio_duration:
            return False
        # if the duration of the transcript exceeds that of the audio file
        first_segment = transcript['segments'][0]
        transcript_duration = float(last_segment['endTime'][:-1]) - float(first_segment['startTime'][:-1])
        if transcript_duration > audio_duration:
            return False

        return True

    def validate_transcript_metadata_duration(self, transcript, metadata):
        """ Validates that the length of the transcript does not exceed the spjall metadata duration """
        # The Tiro transcript must always be shorter or equal to the metadata duration.
        if transcript['metadata']['recordingDuration'] is None:
            t_id = self.get_transcript_id(transcript)
            convo, speaker = self.get_subject_data(transcript)
            print("Duration of transcript {} is set as null.".format(t_id))
            return False
        if float(transcript['metadata']['recordingDuration'][:-1]) > float(metadata['duration_seconds']):
            return False

        return True

def load_json(json_file):
    """ Loads data from a JSON file """
    json_obj = open(json_file)
    data = json.load(json_obj)
    json_obj.close()

    return data

def write_json_to_file(json_object, filename):
    """ Writes a JSON object to a file, mostly for testing as it is """
    with open(filename, 'w') as outfile:
        json.dump(json_object, outfile, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('urls_file')
    parser.add_argument('token_file')

    args = parser.parse_args()

    urls = load_json(args.urls_file)
    token = load_json(args.token_file)

    extract = Extraction(urls, token)
    print("Recordings transcribed: {:.2f}%".format(extract.get_progress()))

    # extract.make_conversation_directory()

    # transcript = extract.get_transcript_by_id(urls['test_id'])

    # duration = extract.get_total_duration_of_speech(transcript)
    # # print("Total:", duration, "seconds", "=", duration/60, "minutes")

    # print("Transcript is valid:", extract.validate_transcript_duration(transcript))


