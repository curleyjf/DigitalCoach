import os
import moviepy.editor as mp
import pandas as pd
from configs.definitions import ROOT_DIR


def _build_timeline_intervals_sentiment(sent_analysis_lst):
    """
    Iterates through the sentiment analysis list from the
    AssemblyAI Audio results to construct a list of lists
    in which the inner list corresponds to the format of
    [start_in_ms, end_in_ms, audio_sentiment_of_interval]
    """
    timeline = []
    for k in sent_analysis_lst:
        interval = [k["start"], k["end"], k["sentiment"]]
        timeline.append(interval)
    timeline.sort(key=lambda x: x[0])
    return timeline


def build_timeline_interval_facial(facial_data):
    """
    Builds the facial data timeline.
    """
    df = pd.DataFrame(data=facial_data["timeline"])
    max_val_index = df.idxmax(axis=1)
    emotion_per_frame = [i for i in max_val_index]
    facial_timeline = {
        k: v
        for k, v in zip(list(range(facial_data["total_frames"])), emotion_per_frame)
    }
    return facial_timeline


def _emotion_sentiment_match(start, end, interval_length, facial_timeline):
    try: 
        return [
            facial_timeline[start // interval_length],
            facial_timeline[end // interval_length],
        ]
    except Exception as _: 
        print('Running into an exception in sentiment matching....')
        print(facial_timeline)
        print(start, end, interval_length)
        print(start // interval_length)
        print(end // interval_length)
        return [-1, -1]

def av_timeline_resolution(clip_length, facial_data, audio_sentiments):
    """
    It takes the audio and facial data, and creates a timeline of the emotions and sentiments of the
    video
    
    :param clip_length: The length of the video in seconds
    :param facial_data: a dictionary containing the facial data
    :param audio_sentiments: a list of tuples, each tuple containing the start and end time of a segment
    of audio, and the sentiment of that segment
    :return: A list of dictionaries.
    """
    total_frames = facial_data["total_frames"]
    fps = round(total_frames / clip_length)
    interval_length = 1000 // fps
    audio_timeline = _build_timeline_intervals_sentiment(audio_sentiments)
    facial_timeline = build_timeline_interval_facial(facial_data)
    timeline = []
    for stats in audio_timeline:
        entry = {
            "start": stats[0],
            "end": stats[1],
            "audioSentiment": stats[2],
            "facialEmotion": _emotion_sentiment_match(
                stats[0], stats[1], interval_length, facial_timeline
            ),
        }
        timeline.append(entry)
    
    timeline = list(filter(lambda x: x['facialEmotion'] != [-1, -1], timeline))
    return timeline


def extract_audio(fname, des_fname):
    """
    It takes a video file, extracts the audio, and returns the path to the audio file and the length of
    the video clip. Converting video to mp3. Ensure ffmpeg is installed and the video path is correct. 
    
    :param fname: The name of the file you want to extract audio from
    :param des_fname: The name of the file you want to save the audio as
    :return: A dictionary with the path to the file and the clip length in seconds.
    """
    path = os.path.join(ROOT_DIR, "data", fname)
    des_path = os.path.join(ROOT_DIR, "data", des_fname) 
    try: 
        mv_clip = mp.VideoFileClip(path) 
        mv_clip.audio.write_audiofile(des_path)
        return {
            "path_to_file": str(des_path),
            "clip_length_seconds": mv_clip.duration,
        }
    except OSError as exception:
        return {"errors": str(exception)}


def read_audio_file(file_path):
    """
    It reads the audio file in chunks of 5MB and yields the data
    
    :param file_path: The path to the audio file
    """
    with open(file_path, "rb") as f:
        while True:
            data = f.read(5242880)
            if not data:
                break
            yield data
