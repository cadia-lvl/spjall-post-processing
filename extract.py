# Author: Lára Margrét H Hólmfríðardóttir

import requests
import json
import argparse
import re
import os
import shutil


class Extraction:
    def __init__(self, urls, token):
        self.headers = {'Authorization': 'Bearer ' + token['API_TOKEN']}
        self.urls = urls
        self.transcripts = self.extract_transcripts()
        # self.invalid_transcripts = []
        # self.valid_transcripts = []

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

    def get_subject_data(self, transcript):
        """ Gets subject data (convo and speaker) of a transcript """
        t_id = self.get_transcript_id(transcript)
        t_obj = self.get_transcript_by_id(t_id)
        # Split on _ or .
        convo, _, speaker, _ = re.split('_|\.', t_obj['metadata']['subject'])

        return convo, speaker

    def get_transcript_id(self, transcript):
        """ Gets the id of a transcript """
        _, transcript_id = transcript['name'].split("/")

        return transcript_id

    def get_audio_file_from_uri(self, transcript, filepath):
        """ Downloads the audio file from the uri of a transcript"""
        # response = requests.get(transcript['uri'], headers=self.headetrs)
        t_id = self.get_transcript_id(transcript)
        t = self.get_transcript_by_id(t_id)
        response = requests.get(t['uri'])
        with open('{}.wav'.format(filepath), 'wb') as f:
            f.write(response.content)

    def get_demographics(self, convo, speaker):
        """ Gets the JSON demographics of a speaker in a conversation """
        response = requests.get(urls['samromur_url'] + '/{}/{}_client_{}.json'.format(convo, convo, speaker))
        t_demographics = response.json()

        # write_json_to_file(t_demographics, 't_demographics.json')

        return t_demographics

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
        print("Creating a directory for each conversation. This might take a moment...")
        convo_dir_log = 'conversations_dir_log.txt'
        validation_log = 'validation_log.txt'
        self.clear_log(convo_dir_log)
        self.clear_log(validation_log)
        keep_flag = False

        try:
            os.mkdir("conversations")
        # If conversations directory already exists, give user a choice to clear the directory, or keep existing files.
        # Kept files will not be overwritten.
        except FileExistsError:
            print("Conversations directory already exists.")
            print("\tc - Clear conversations directory and start from scratch.")
            print("\tk - Keep existing conversations, and only add new ones.")
            print("\tq - Quit and cancel.")
            while True:
                option = input("Enter c to clear, or k to keep: ")
                if option == "c":
                    print("Clearing conversations directory...")
                    for dir in os.listdir("conversations"):
                        shutil.rmtree("conversations/" + dir)
                    break
                elif option == "k":
                    print("Keeping old files, and only adding new ones...")
                    keep_flag = True
                    break
                elif option == "q":
                    return
                else:
                    print("Please enter a valid option.")

        count = 0
        not_added = 0
        added = 0
        if keep_flag:
            kept = 0
        for t in self.transcripts:
            transcript_id = self.get_transcript_id(t)
            # If the transcript is invalid, a test transcript, or unifinished, it will not be added to a directory.
            # if t in self.invalid_transcripts:
            if not self.validate_transcript(t, validation_log):
                self.write_to_log("Transcript {} is invalid and was not added to directory.".format(transcript_id), convo_dir_log)
                not_added += 1
            # Remove if guaranteed that no test transcript has __spjallromur__/TRANSCRIBED/PROOFREAD tag, otherwise the subject parsing causes problems.
            # elif t['metadata']['subject'] == "Test Spegillinn":
            #     self.write_to_log("Transcript {} is a test transcript and was not added to directory.".format(transcript_id), convo_dir_log)
            #     not_added += 1
            elif t in self.filter_transcripts("TODO") or t in self.filter_transcripts("INPROGRESS"):
                self.write_to_log("Transcript {} is unfinished and was not added to directory.".format(transcript_id), convo_dir_log)
                not_added += 1
            # If the transcript has been marked as transcribed or proofread, add it to a corresponding directory.
            elif t in self.filter_transcripts("TRANSCRIBED") or t in self.filter_transcripts("PROOFREAD"):
                # Get the transcript by id to access the uri for the audio file
                transcript = self.get_transcript_by_id(transcript_id)
                convo, speaker = self.get_subject_data(transcript)
                t_demographics = self.get_demographics(convo, speaker)
                # Where the file should be written
                filepath = "conversations/{}/speaker_{}_convo_{}".format(convo, speaker, convo)
                try:
                    os.mkdir("conversations/{}".format(convo))
                    self.get_audio_file_from_uri(transcript, filepath)
                    write_json_to_file(t_demographics, filepath + "_demographics.json")
                    write_json_to_file(transcript, filepath + "_transcript.json")
                    added += 1
                # If a directory for a conversation exists, just add the corresponding files.
                except FileExistsError:
                    # If user does not want to overwrite existing files, do nothing to those files.
                    if keep_flag and (os.path.exists(filepath + "_demographics.json") or os.path.exists(filepath + "_transcript.json") or os.path.exists(filepath + ".wav")):
                        kept += 1
                    else:
                        self.get_audio_file_from_uri(transcript, filepath)
                        write_json_to_file(t_demographics, filepath + "_demographics.json")
                        write_json_to_file(transcript, filepath + "_transcript.json")
                        added += 1
                # If the conversation name contains a file path.
                except FileNotFoundError:
                    self.write_to_log("Could not create directory for {}. Transcript name contains a filepath.".format(convo), convo_dir_log)
                    not_added += 1
            else:
                self.write_to_log("Transcript {} has unapproved tags and was not added to directory.".format(transcript_id), convo_dir_log)
                not_added += 1

            count += 1
            print("{}/{} transcripts processed.".format(count, len(self.transcripts)))

        if keep_flag:
            print("{} existing files kept and not overwritten.".format(kept))
        if not_added > 0:
            print("{} transcripts were not added to a directory. Refer to {} and {} for further information.".format(not_added, convo_dir_log, validation_log))
        print("Completed. {} transcripts were added to their corresponding directory.".format(added))

    """
    Transcript validation
    """

    # Was intended to validate before making directories, but validation happens inside the for loop in make_conversation_directory to save time.
    # Not being used as it is, commented out in case it is needed later.

    # def validate_transcripts(self):
    #     """ Validates the extracted transcripts and sets invalid_transcripts and valid_transcripts """
    #     print("Validating transcripts...")
    #     validation_log = "validation_log.txt"
    #     self.clear_log(validation_log)
    #     count = 0
    #     invalid = []

    #     for t in self.transcripts:
    #         t_id = self.get_transcript_id(t)

    #         if not self.validate_transcript(t, validation_log):
    #             invalid.append(t)

    #         count += 1
    #         print("{}/{} validated.".format(count, len(self.transcripts)))


    #     print("{} transcripts are invalid.".format(len(invalid)))
    #     self.invalid_transcripts = invalid

    #     valid = [obj for obj in self.transcripts if (obj not in invalid)]
    #     self.valid_transcripts = valid

    #     # write_json_to_file(invalid, "testing/invalid.json")
    #     # write_json_to_file(valid, "testing/valid.json")

    #     print("Validation complete.")
    #     print("{} valid transcripts, and {} invalid transcripts. Refer to validation_log.txt for further information.".format(len(valid), len(invalid)))

    def validate_transcript(self, transcript, log):
        """ Validates a single transcript """
        t_id = self.get_transcript_id(transcript)
        # t_obj = self.get_transcript_by_id(t_id)

        if transcript in self.filter_transcripts("INVALID"):
            self.write_to_log("Transcript {} was tagged INVALID.".format(t_id), log)
            return False
        # Transcript duration validation
        t_duration = self.validate_transcript_duration(transcript, log)
        if not t_duration:
            return False
        # Demographics duration validation
        convo, speaker = self.get_subject_data(transcript)
        t_demo = self.get_demographics(convo, speaker)
        t_demographics_duration = self.validate_transcript_demographics_duration(transcript, t_demo, log)
        if not t_demographics_duration:
            return False
        t_speech_duration = self.validate_duration_of_speech(transcript, log)
        if not t_speech_duration:
            return False
        # TODO: Other validation checks.

        return True

    def validate_transcript_duration(self, transcript, log):
        """ Validates the length of the transcript. Returns False if invalid, True otherwise. """
        t_id = self.get_transcript_id(transcript)
        t_obj = self.get_transcript_by_id(t_id)

        if t_obj['metadata']['recordingDuration'] is None:
            self.write_to_log("Transcript {} has recordingDuration set as null.".format(t_id), log)
            return False

        try:
            # This can only be validated for finished transcriptions
            if transcript in self.filter_transcripts("TRANSCRIBED") or transcript in self.filter_transcripts("PROOFREAD"):
                audio_duration = float(t_obj['metadata']['recordingDuration'][:-1])
                # if the last segment time stamps exceed that of the audio duration
                last_segment = t_obj['segments'][-1]
                if float(last_segment['endTime'][:-1]) > audio_duration:
                    self.write_to_log("Transcript {} exceeds the audio duration. Last segment ends at: {}, audio duration: {}.".format(t_id, last_segment['endTime'], audio_duration))
                    return False
                # if the duration of the transcript exceeds that of the audio file
                first_segment = t_obj['segments'][0]
                transcript_duration = float(last_segment['endTime'][:-1]) - float(first_segment['startTime'][:-1])
                if transcript_duration > audio_duration:
                    self.write_to_log("Transcript {} exceeds the audio duration. Transcript duration: {}, audio duration: {}.".format(t_id, transcript_duration, audio_duration))
                    return False

            return True

        except TypeError as e:
            self.write_to_log("Transcript {} has segment timestamps with wrong type. Could not calculate transcript duration.".format(t_id, e), log)
            return False

    def validate_transcript_demographics_duration(self, transcript, t_demographics, log):
        """ Validates that the length of the transcript does not exceed the spjall demographics duration """
        # The Tiro transcript must always be shorter or equal to the demographics duration.
        t_id = self.get_transcript_id(transcript)
        t_obj = self.get_transcript_by_id(t_id)

        if t_obj['metadata']['recordingDuration'] is None:
            self.write_to_log("Transcript {} has recordingDuration set as null.".format(t_id), log)
            return False
        if float(t_obj['metadata']['recordingDuration'][:-1]) > float(t_demographics['duration_seconds']):
            self.write_to_log("Transcript {} duration exceeds the demographics duration.".format(t_id), log)
            return False

        return True

    def get_duration_of_speech(self, transcript):
        """ Gets the total duration of speech in seconds by adding the duration of each segment in the transcript. """
        duration = 0

        for segment in transcript['segments']:
            # [:-1] because the last letter of the string is always s for seconds. Then convert to float for subtraction.
            segment_duration = float(segment['endTime'][:-1]) - float(segment['startTime'][:-1])
            duration += segment_duration

        return duration

    # TODO: Fix null timestamps, possibly with tiro alignment jobs, so that transcripts can be properly validated.
    def send_tiro_alignment_job(self, transcript):
        """ Sends tiro alignment request for a transcript in an attempt to fix NULL timestamps """
        body = {
            "transcript": "{}".format(transcript['name'])
        }
        response = requests.post(urls['tiro_alignment_submit_url'], data=json.dumps(body), headers=self.headers)
        res = response.json()

        return res

    def get_tiro_alignment_jobs(self):
        """ Gets tiro alignment jobs """
        response = requests.get(urls['tiro_alignment_status_url'], headers=self.headers)
        res = response.json()

        return res

    def get_tiro_alignment_job(self, job_id):
        """ Gets the status of a specific alignment job """
        # TODO: Error 13 while writing this part of the script prevented progress.
        # I'm not sure this works as it is so some changes might have to be made, as well as updating the transcript
        # with the complete alignment job so that the transcript can be properly validated (if the alignment job fixes segment null timestamps)

        response = requests.get(urls['tiro_alignment_status_url'] + "/" + job_id, headers=self.headers)
        res = response.json()

        return res

    def ffmpeg_duration_of_speech(self, transcript):
        """ Uses ffmpeg's detectsilence to log intervals of silence to get duration of speech. """

        self.get_audio_file_from_uri(transcript, "audio")

        # Detects silences of length 0.25s or longer. A silence is -35dB or less. Loads into a text file for parsing.
        os.system("ffmpeg -i {} -af silencedetect=n=-35dB:d=0.25,ametadata=print:file=silencedetect.txt -f null -".format("audio.wav"))
        silence_duration = self.parse_silence("silencedetect.txt")
        t_duration = float(transcript['metadata']['recordingDuration'][:-1])
        speech_duration = t_duration - silence_duration
        os.remove("audio.wav")
        os.remove("silencedetect.txt")

        return speech_duration

    def parse_silence(self, filepath):
        """ Parses the silencedetect file for the silence durations. """
        silence_duration = 0
        with open(filepath, 'r') as log:
            for line in log:
                if "silence_duration" in line:
                    _, duration = line.split("=")
                    silence_duration += float(duration)

        return silence_duration

    def validate_duration_of_speech(self, transcript, log):
        """ If the difference between the two durations is equal to or greater than 60 seconds, return False. """
        error_threshold = 60
        t_id = self.get_transcript_id(transcript)
        t_obj = self.get_transcript_by_id(t_id)

        try:
            t_speech = self.get_duration_of_speech(t_obj)
            t_ffmpeg_speech = self.ffmpeg_duration_of_speech(t_obj)

        except TypeError as e:
            self.write_to_log("Transcript {} has segment timestamps with wrong type. Could not calculate transcript duration.".format(t_id, e), log)
            return False
        diff = t_speech - t_ffmpeg_speech

        if abs(diff) >= error_threshold:
            self.write_to_log("Duration of speech for transcript {} is invalid. Measured and calculated difference is too great.".format(t_id), log)
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
    # extract.validate_transcripts()

    extract.make_conversation_directory()

