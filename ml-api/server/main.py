"""
Main Flask application as well as routes of the app.
"""
from server import app
import uuid
import redis
from threading import Thread
from rq import Queue
from flask import Flask, jsonify, request
from flask_cors import CORS
from helpers.download_url import download_video_link
from helpers.score import create_answer
from .db_monitor import poll_connection

import json
import re

import ffmpeg
import os

CORS(app)
r = redis.Redis()
q = Queue(connection=r)


@app.before_first_request
def launch_polling_script():
    Thread(target=poll_connection, args=(r,), daemon=True).start()
    print("Launched polling script in different thread.")


@app.route("/", methods=["GET"])
def index():
    """
    Home route.
    """
    return "Welcome to the ML API for Digital Coach ayayay"


@app.route("/results/<job_id>", methods=["GET"])
def get_results(job_id):
    """
        GET route that returns results of a job.
        """
    job = q.fetch_job(job_id)
    if job is None:
        return jsonify(message="Job not found.")
    if job.is_finished:
        result = job.result
        e_result = eval(result)
        json_string = json.dumps(e_result)
        return jsonify(result=json.loads(json_string))
    else:
        return jsonify(message="Job has not finished yet.")


@app.route("/predict", methods=["POST"])
def predict():
    """
    POST route that returns total text, audio and video predictions.
    """
    req = request.get_json() # Video URL  
    # Download the video from the firebase URL 
    video_url = req['videoUrl'] 
    if not video_url:
        return jsonify(errors="Required fields not in request body.") 
    download = download_video_link(video_url) # Download video from URL, returns path to video
    if "errors" in download:
        return jsonify(message="Download Failed.") 
    print("Download Successful!")
    content = {
        "fname": "video.mp4",
        "rename": str(uuid.uuid4()) + ".mp3" 
    }
    job = q.enqueue(create_answer, content)
    message = "Task " + str(job.get_id) + " added to queue at " + str(job.enqueued_at) + "." 
    return jsonify(message=message) 



''

waitress-serve --listen=*:8000 server.wsgi:app

rqworker -w rq_win.WindowsWorker

'''
