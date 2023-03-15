from pytube import YouTube
import os
import openai
import configparser

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

print(text)

