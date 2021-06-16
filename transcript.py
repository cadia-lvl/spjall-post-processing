import os
import requests

class Transcript:
    def __init__(self, json_transcript, headers):
        self.json = json_transcript
        self.speech_duration = self.get_total_duration_of_speech()
        self.headers = headers
    

    def get_total_duration_of_speech(self):
        """ Gets the total duration of speech (in seconds) by adding the duration of all segments of the transcripts together """
        duration = 0
        for segment in self.json['segments']:            
            # [:-1] because the last letter of the string is always s for seconds. Then convert to float for subtraction.
            segment_duration = float(segment['endTime'][:-1]) - float(segment['startTime'][:-1])
            duration += segment_duration
            
        return duration

    def get_audio_file_from_uri(self):
        """ Downloads the audio file from the uri """
        response = requests.get(self.json['uri'], headers=self.headers)
        with open('audio.wav', 'wb') as f:
            f.write(response.content)

    def validate_transcript_duration(self):
        """ Validates the length of the transcript. Returns False if invalid, True otherwise. """
        audio_duration = float(self.json['metadata']['recordingDuration'][:-1])
        # if the speech duration measures longer than the audio duration
        if self.speech_duration > audio_duration:
            return False
        # if the last segment time stamps exceed that of the audio duration
        last_segment = self.json['segments'][-1]
        if float(last_segment['endTime'][:-1]) > audio_duration:
            return False
        # if the duration of the transcript exceeds that of the audio file
        first_segment = self.json['segments'][0]
        transcript_duration = float(last_segment['endTime'][:-1]) - float(first_segment['startTime'][:-1])
        if transcript_duration > audio_duration:
            return False
        
        return True

    
    # def verify_duration_of_speech(self):
        # it is probably best to find a way to use ffmpeg for this
        # TODO: Normalize audio file ?
    #     os.system("ffmpeg -i audiofile.wav -af silencedetect=n=-50dB:d=3,ametadata=print:file=log.txt -f null -")
    #     # os.system("ffprobe -v quiet -print_format compact=print_section=0:nokey=1:escape=csv -show_entries format=silence_duration output.txt")