import urllib.request
import os
from configs.definitions import ROOT_DIR
import requests


def download_video_link(url):
    """
    Downloads a video from a given url and saves it to the data folder.
    (Depreciated)
    
    :param url: The URL of the video you want to download
    :return: the path to the downloaded file.
    """
    dest = os.path.join(ROOT_DIR, "data", "video.mp4")
    print(url) 
    try:
        urllib.request.urlretrieve(url, dest)     
        return dest
    except Exception as e:
        return {"errors": e}

def download_video(video_url):
    """
    Downloads a video from a given url and saves it to the data folder.
    
    :param url: The URL of the video you want to download
    :return: the path to the downloaded file.
    """
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open("data/video.mp4", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print("Video downloaded successfully.")
    else:
        print("Failed to download video.")


