# spjall-post-processing
To start out, we will automate the submission and extraction flow of audio files to and from Tiro.
1. Automatically submit audio files from Spjall to Tiro's editor.
2. Then, automatically extract the transcript from Tiro for post-processing.


## Structure
List the contents/folder structure of the spjallromur directory.


## Packages and Installation
List packages required to run the scripts, and how to install them.


## Running
Steps to run the scripts.


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


## Task List
- [ ] Automatically send audio files to the Tiro API.
- [ ] Automatically receive transcripts from the Tiro API.
- [ ] Get the total duration of speech from the transcripts and verify it.
- [ ] Create a list out of vocabulary words based on a pronunciation dictionary.
- [ ] Validate that the transcripts has proper tags, i.e. transcribed, proofread, etc.
- [ ] Validate that the duration of the transcripts does not exceed that of the corresponding audio files.
- [ ] Validate that the timestamps for speech do not correlate with any durations of silence over 30 seconds long.
- [ ] Create a folder for each conversation.
- [ ] Validate that the transcript, audio, and metadata names follow the correct naming scheme.
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
- [ ] Redact "steini" from any conversations which were spoken before May 3rd.


## Authors and Contacts
Authors and contacts for the dataset

## License
- Apache 2.0

## Acknowledgements
