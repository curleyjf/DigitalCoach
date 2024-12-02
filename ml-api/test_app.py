import pytest
from flask import json
from app import app
import requests_mock
from models import BigFiveScores


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# def test_predict_endpoint(client):
#     with requests_mock.Mocker() as m:
#         m.post('/predict', json={'message': 'Task 123 added to queue at 2023-11-11 00:00:00.'})
#         response = client.post('/predict', json={
#             'videoUrl': '../data/video.mp4', 
#         })
#         assert response.status_code == 200
#
#
# def test_big_five_feedback_endpoint(client):
#     with requests_mock.Mocker() as m:
#         m.post('/big-five-feedback', json={'message': 'Task 123 added to queue at 2023-11-11 00:00:00.'})
#         response = client.post('/big-five-feedback', json={ 
#                 'o': 2.5,
#                 'c': 4.2,
#                 'e': -1.8,
#                 'a': 3.1,
#                 'n': -2.7 
#         })
#
#         assert response.status_code == 200
#         feedback = response.json['feedback']
#         assert len(feedback) == 5 
#         print(feedback)
#
#         assert 'With an Openness score between -3 and 3, you are somewhat open to new experiences and creative, but you still enjoy some structure and consistency.' in feedback[0]
#         assert 'With a Conscientiousness score greater than 3, you are always prepared, keep things in order and are very goal driven.' in feedback[1]
#         assert 'With an Extraversion score between -3 and 3, you enjoy your personal time but also like the occasional exciting activity or large gathering.' in feedback[2]
#         assert 'With an Agreeableness score greater than 3, you care about others, are always ready to help them and see the best in them.' in feedback[3]
#         assert 'With a Neuroticism score between -3 and 3, you have some confidence in yourself and can stay calm in somewhat stressful situations, but still carry self doubts.' in feedback[4]
#
#
# def test_star_scores_endpoint(client):
#     with requests_mock.Mocker() as m:
#         m.post('/star-feedback', json={'message': 'Task 123 added to queue at 2023-11-11 00:00:00.'})
#         response = client.post('/star-feedback', json={
#             "text": "This is an example sentence that I was required to make for this assignment. I was tasked with creating this sentence. I wrote this sentence to be used as an example for the prompt. I used the word 'sentence' and explained the context multiple times to activate the action part of the sentence. This sentence made a good example of the prompt and showed how the model works."
#
#         }) 
#         print(response.json) # use -s to display print.
#         assert response.status_code == 200
#


