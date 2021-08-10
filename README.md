# spjall-post-processing
To start out, we will automate the submission and extraction flow of audio files to and from Tiro.
1. Automatically submit audio files from Spjall to Tiro's editor.
2. Then, automatically extract the transcript from Tiro for post-processing.


## Structure

The corpus has the following format:
```
        README.md
        conversations/
        xxxx/
            speaker_x_convo_xxxx_demographics.json
            speaker_x_convo_xxxx_transcript.json
            speaker_x_convo_xxxx.wav
```

## Packages and Installation
List packages required to run the scripts, and how to install them.


## Running
You need to have your versions of the files within config.

The script to submit conversations to [Tiro](https://tal.tiro.is) is run as a
cron job using the following command:

```
python3 uploading.py
```

To run the post-processing script, currently, you run it with the following
command:
```
python3 extract.py config/urls.json config/token.json
```


## Statistics
To add:
- Number of speakers
- Total duration of speech
- Demographics (gender, age range, native and second language speakers)


## Notes
- Each participant's recording shall be coordinated with other participants' recordings. These files shall be converted to .wav files where there is one channel for each participant.
- Participants have the option of marking portions they do not want included in published data. These portions can be 'beeped' or cut out using tools such as Audacity.
- Each participant has their own .json file, where their portion of the conversation is written.
- Files should be named as follows:
  - Audio files: convo_XXXX.wav, e.g. convo_0001.
  - Text files: speaker_X_convo_XXXX.json, e.g. speaker_1_convo_0001.json
- There should only be a single point of entry for users.
- Do not save any credentials or urls to the repo. (spjall, tiro, or account access)


## Task List
- [x] Automatically send audio files to the Tiro API.
- [x] Automatically receive transcripts from the Tiro API.
- [ ] Get the total duration of speech from the transcripts and verify it.
- [ ] Create a list out of vocabulary words based on a pronunciation dictionary.
- [ ] Validate that the transcripts has proper tags, i.e. transcribed, proofread, etc.
- [x] Validate that the duration of the transcripts does not exceed that of the corresponding audio files.
- [ ] Submit a tiro alignment job for any transcripts with segments which have a null timestamp (the server is slow)
- [ ] Validate that the timestamps for speech do not correlate with any durations of silence over 30 seconds long.
- [x] Create a folder for each conversation.
- [ ] Validate that the transcript, audio, and demographics files follow the correct naming scheme.
- [ ] Make sure that the dataset meets both the clarin and the ldc standard.
- [ ] Create a running total of transcribed conversation count out of the total conversation count.
- [ ] Create a list of out of vocabulary words based on an existing pronunciation dictionary
- [ ] Create a README for the dataset. Not this one
  - [ ] Add a description (both icelandic and english)
  - [ ] List the dataset authors and contact people
  - [ ] List what's in the spjallrómur dataset directory structures and the file contents
  - [ ] Add the statistics mentioned above (speakers, speech duration, demographics data)
- [ ] Automatically find the conversation topics from the following:
  - Technology
  - Politics
  - Sports
  - Food
  - Culture
  - Weather
  - Other
- [x] Remove reference from the demographics metadata
- [x] Remove ritari keyword from the transcript files
- [ ] Remove uri references in the transcript files which refer to a non-redacted version of the audio.
- [ ] Redact audio of personal information
  - [ ] Redact "steini" from any conversations which were spoken before May 3rd.



## Authors
- Lára Margrét H. Hólmfriðardóttir
- Málfriður Anna Eiríksdóttir
- Judy Y. Fong lvl@judyyfong.xyz


## License
- Apache 2.0

## Acknowledgements
