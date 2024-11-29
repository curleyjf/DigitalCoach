from re import A
from helpers.text_processor import clean_text
from helpers.text_predict import predict_text_structure
from models.models import detect_emotions, detect_audio_sentiment
from helpers.av_processing import extract_audio, av_timeline_resolution
from helpers.statistics import (
    calculate_top_three_facial_with_count,
    calculate_overall_audio_sentiment,
    grab_top_five_keywords,
    compute_aggregate_score,
)
from helpers.file_management import (
    move_cv_files,
    cleanup_data_folder,
    cleanup_data_persist_video,
)


def _score_text_structure(audio_answer):
    """
    score how structured the user's answers are.
    """
    print("audio_answer", audio_answer)
    sentiments = audio_answer["sentiment_analysis"]
    text = ""
    for i in sentiments:
        text += i["text"] 
    cleaned = clean_text(text)
    predictions = predict_text_structure(cleaned)
    return {"percent_prediction": predictions[0], "binary_prediction": predictions[1], "output_text": text}


def _score_audio(content):
    """
    score user's audio.
    """
    if "fname" not in content or "rename" not in content:
        return {"errors": "File name and rename does not exist"}
    fname, rename = content["fname"], content["rename"], 
    audio = extract_audio(fname, rename)
    if "errors" in audio:
        return {"errors": audio["errors"]}
    audio_file_path = audio["path_to_file"]
    sentiment = detect_audio_sentiment(audio_file_path)
    sentiment["clip_length_seconds"] = audio["clip_length_seconds"]
    if "errors" in sentiment:
        return {"errors": sentiment["errors"]}
    return sentiment


def _score_facial(content):
    """
    score user's facial expressions
    """
    if "fname" not in content:
        return {"errors": "Video file name does not exist"}
    video_fname = content["fname"]
    total_emotion_score = detect_emotions(video_fname)
    move_cv_files()
    cleanup_data_persist_video()
    if "errors" in total_emotion_score:
        return {"errors": total_emotion_score}
    return total_emotion_score


def _score_bigFive(audio_answer, facial_stats, text_answer):
    oScore, cScore, eScore, aScore, nScore = 0, 0, 0, 0, 0
    temp_avg = 0
    for keyword in grab_top_five_keywords(audio_answer):
        if len(keyword["text"]) > 10:
            temp_avg += 10
        else:
            temp_avg += len(keyword["text"])
    overallSentiment = calculate_overall_audio_sentiment(audio_answer)
    isStructuredPercent = text_answer["percent_prediction"]
    topThreeFacial = facial_stats
    oScore += (temp_avg/5) - 7
    cScore += isStructuredPercent*10 - 5
    aScore += (temp_avg/25) - 1
    nScore += isStructuredPercent*10 - 6
    if topThreeFacial[0] == 'happy':
        aScore += 2
        nScore += 1
    for emotion in topThreeFacial:
        if (emotion == 'sad' or emotion == 'fear' or emotion == 'disgust' or emotion == 'angry'):
            oScore -= 2
            eScore -= 1
            aScore -= 2
            nScore -= 1
        elif emotion == 'neutral':
            eScore += .5
            aScore -= .5
        else:
            oScore += .5
            eScore += 1
            aScore += 1
            nScore += 1
    if overallSentiment == "NEGATIVE":
        eScore -= 2
        aScore -= 2
        nScore -= 1
    elif overallSentiment == "NEUTRAL":
        eScore += .5
        aScore -= .5
        nScore -= .5
    else:
        eScore += 2
        aScore += 1
    bigFive = {
        "o": round(oScore),
        "c": round(cScore),
        "e": round(eScore),
        "a": round(aScore),
        "n": round(nScore),
    }
    return bigFive


def create_answer(content): 
    facial_answer = _score_facial(content) 
    audio_answer = _score_audio(content)  
    text_answer = _score_text_structure(audio_answer)
    timeline = av_timeline_resolution(
        audio_answer["clip_length_seconds"],
        facial_answer,
        audio_answer["sentiment_analysis"],
    )
    (
        facial_stats,
        top_stat,
        second_stat,
        third_stat,
    ) = calculate_top_three_facial_with_count(facial_answer)
    bigFive = _score_bigFive(audio_answer, facial_stats, text_answer)
    result = {
        "timeline": timeline,
        "isStructured": text_answer["binary_prediction"],
        "isStructuredPercent": text_answer["percent_prediction"],
        "facialStatistics": {
            "topThreeEmotions": facial_stats,
            "frequencyOfTopEmotion": top_stat,
            "frequencyOfSecondEmotion": second_stat,
            "frequencyOfThirdEmotion": third_stat,
        },
        "overallFacialEmotion": facial_stats[0],
        "overallSentiment": calculate_overall_audio_sentiment(audio_answer),
        "topFiveKeywords": grab_top_five_keywords(audio_answer),
        "bigFive": bigFive,
    }
    result["aggregateScore"] = compute_aggregate_score(result)
    response = {}
    response["evaluation"] = result
    response["text_analysis"] = text_answer 
    # response["userId"] = content["user_id"]
    # response["interviewId"] = content["interview_id"]
    # response["questionId"] = content["question_id"]
    # response["answerId"] = content["answer_id"]
    cleanup_data_folder()
    return str(response)
