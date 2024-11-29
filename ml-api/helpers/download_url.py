import urllib.request
import os
from configs.definitions import ROOT_DIR


def download_video_link(url):
    """
    Downloads a video from a given url and saves it to the data folder.
    
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
