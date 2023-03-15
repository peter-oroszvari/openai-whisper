from pytube import YouTube
import os
import openai
import configparser
import spacy


config = configparser.ConfigParser()
config.read('config.ini')

openai.api_key = config.get('openai', 'api_key')

url = input("Enter the URL of the YouTube video: ")
yt = YouTube(url) 

#  Download the video
stream = yt.streams.get_highest_resolution()
video_path = stream.download()

#  Define paths
audio_path = os.path.splitext(video_path)[0] + ".mp3"

# Extract audio and save as mp3
os.system(f"ffmpeg -i '{video_path}' -vn -acodec libmp3lame '{audio_path}'")

#  Delete the video file
os.remove(video_path)

audio_file= open(audio_path, "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file) # response_format="srt"
text = transcript.text.encode('utf-8').decode('utf-8') 

# Load spaCy's Hungarian language model
nlp = spacy.load("hu_core_news_lg")

# Use spaCy to split the text into individual sentences
doc = nlp(text)
sentences = [sent.text for sent in doc.sents]

# Define the maximum number of tokens per API request
max_tokens = 2048

chunks = []
current_chunk = ""
for sentence in sentences:
    if len(current_chunk + sentence) < max_tokens:
        current_chunk += sentence
    else:
        chunks.append(current_chunk)
        current_chunk = sentence
if current_chunk:
    chunks.append(current_chunk)
    
translations = []
for chunk in chunks:
    translation = openai.Completion.create(
        engine="text-davinci-002",
        prompt=(f"Translate the following Hungarian text to English:\n\n{chunk}\n\nTranslation: "),
        temperature=0.5,
        max_tokens=max_tokens,
        n = 1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    translations.append(translation.choices[0].text.strip())

print('\n'.join(translations))

print(text)

