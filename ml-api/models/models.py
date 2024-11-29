import os
import time
import pickle
import requests
from fer import Video, FER
from dotenv import load_dotenv
from configs.definitions import ROOT_DIR
from helpers.av_processing import read_audio_file
from urllib.parse import urlparse
import transformers
import json

TEXT_MODEL = pickle.load(open("models/text_model.pkl", "rb"))
TFIDF_MODEL = pickle.load(open("models/tfidf_model.pkl", "rb"))
LABEL_MAPPING = json.load(open("models/label_mapping.json", "r")) 
STAR_MODEL, STAR_TOKENIZER = pickle.load(open("models/model_tokenizer.pkl", "rb"))

env_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(env_path)

# Use fer to detect emotions in a video
def detect_emotions(video_fname, freq=10):
    videofile_path = os.path.join(ROOT_DIR, "data", video_fname)
    print(videofile_path)

    face_detection = FER(mtcnn=True)
    try:
        input_video = Video(videofile_path)
        processed_data = input_video.analyze(
            face_detection, display=False, frequency=freq
        )
        vid_df = input_video.to_pandas(processed_data)
        vid_df = input_video.get_first_face(vid_df)
        vid_df = input_video.get_emotions(vid_df)
        sum_emotions = {
            "angry": sum(vid_df.angry),
            "disgust": sum(vid_df.disgust),
            "fear": sum(vid_df.fear),
            "happy": sum(vid_df.happy),
            "sad": sum(vid_df.sad),
            "surprise": sum(vid_df.surprise),
            "neutral": sum(vid_df.neutral),
        }
        timelines = {
            "angry": list(vid_df.loc[:, "angry"]),
            "disgust": list(vid_df.loc[:, "disgust"]),
            "fear": list(vid_df.loc[:, "fear"]),
            "happy": list(vid_df.loc[:, "happy"]),
            "sad": list(vid_df.loc[:, "sad"]),
            "surprise": list(vid_df.loc[:, "surprise"]),
            "neutral": list(vid_df.loc[:, "neutral"]),
        }
        response = {
            "total_frames": len(list(vid_df.loc[:, "angry"])),
            "frame_inference_rate": freq,
            "emotion_sums": sum_emotions,
            "timeline": timelines,
        }
        return response
    except OSError as exception:
        return {"errors": str(exception)}


def detect_audio_sentiment(fname):
    """
    Detects audio sentiment using AssemblyAI API
    """
    print(f"Starting sentiment detection for file: {fname}")
    
    headers = {
        "authorization": os.getenv("AAPI_KEY"),
        "content-type": "application/json",
    }
    print(f"Headers: {headers}")
    
    try:
        res_upload = requests.post(
            os.getenv("UPLOAD_ENDPOINT"), headers=headers, data=read_audio_file(fname)
        )
        print(f"Upload response: {res_upload.status_code}, {res_upload.text}")
        
        upload_url = res_upload.json().get("upload_url")
        print(f"Upload URL: {upload_url}")
        
        if not upload_url:
            print("Error: No upload URL returned")
            return {"errors": "No upload URL returned"}
        
        res_transcript = requests.post(
            os.getenv("TRANSCRIPT_ENDPOINT"),
            headers=headers,
            json={
                "audio_url": upload_url,
                "sentiment_analysis": True,
                "auto_highlights": True,
                "iab_categories": True,
            },
        )
        print(f"Transcript response: {res_transcript.status_code}, {res_transcript.text}")

        transcript_id = res_transcript.json().get("id")
        print(f"Transcript ID: {transcript_id}")
        
        if not transcript_id:
            print("Error: No transcript ID returned")
            return {"errors": "No transcript ID returned"}
        
        polling_endpoint = os.getenv("TRANSCRIPT_ENDPOINT") + "/" + transcript_id
        print(f"Polling endpoint: {polling_endpoint}")
        
        status = ""
        while status != "completed":
            response_result = requests.get(polling_endpoint, headers=headers)
            status = response_result.json().get("status")
            print(f"Polling status: {status}")
            
            if status == "error":
                print("Error reached during polling")
                return {"errors": "Status error reached"}
            elif status != "completed":
                time.sleep(10)

        if status == "completed":
            sentiment_results = response_result.json().get("sentiment_analysis_results")
            highlights_results = response_result.json().get("auto_highlights_result")
            iab_results = response_result.json().get("iab_categories_result")
            response = {
                "sentiment_analysis": sentiment_results,
                "highlights": highlights_results,
                "iab_results": iab_results,
            }
            print(f"Final response: {response}")
            return response

    except Exception as e:
        print(f"Exception occurred: {e}")
        return {"errors": str(e)}

    return {"errors": "Unexpected error"}
