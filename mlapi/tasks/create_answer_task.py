from rq.decorators import job
from typing import List, Optional
from schemas.create_answer import (
    # TextStructureResult,
    TimelineStructure,
    BigFiveScoreResult,
    CreateAnswerEvaluation,
    OverallCompetencyFeedback,
)

# # Redis
# from redisStore.myconnection import get_redis_con
# from redisStore.queue import add_task_to_queue

# # Functions
# from tasks.assemblyai_api import detect_audio_sentiment
# from tasks.detect_emotions import detect_emotions
# from tasks.helpers.create_answer_helpers import (
#     score_text_structure,
#     score_bigFive,
#     compute_aggregate_score,
# )
# from tasks.helpers.av_processing import (
#     av_timeline_resolution,
#     calculate_top_three_facial_with_count,
#     calculate_overall_audio_sentiment,
#     grab_top_five_keywords,
# )
# from tasks.helpers.competency_feedback import generate_competency_feedback
# from utils.logger_config import get_logger
# import time
# from rq.job import Job


# logger = get_logger(__name__)


# def start_audio_analysis_job(video_url: str) -> str:
#     """
#     Start the audio analysis job

#     Args:
#         video_url: URL or path to the video file

#     Returns:
#         str: Job ID
#     """
#     job = add_task_to_queue(detect_audio_sentiment, video_url)
#     logger.info(f"Started audio analysis job: {job.get_id()}")
#     return job.get_id()


# def start_facial_analysis_job(video_url: str) -> str:
#     """
#     Start the facial analysis job

#     Args:
#         video_url: URL or path to the video file

#     Returns:
#         str: Job ID
#     """
#     job = add_task_to_queue(detect_emotions, video_url)
#     logger.info(f"Started facial analysis job: {job.get_id()}")
#     return job.get_id()


# def await_job_result(job_id, timeout=30):
#     job = Job.fetch(job_id, connection=get_redis_con())
#     start_time = time.time()

#     while job.result is None and time.time() - start_time < timeout:
#         time.sleep(0.1)  # Small sleep to avoid hogging CPU
#         job = Job.fetch(job_id, connection=get_redis_con())

#         # Check if job failed
#         if job.is_failed:
#             raise Exception(f"Job failed: {job.exc_info}")

#     if job.result is None:
#         raise TimeoutError(f"Job didn't complete within {timeout} seconds")

#     return job.result


# @job("default", connection=get_redis_con())
def create_answer(
    video_url: str,
    audio_job_id: Optional[str] = None
) -> CreateAnswerEvaluation:
    """
    Creates feedback answer by running or retrieving audio and facial analysis,
    then combining the results.

    Args:
        video_url: URL or path to the video file
        audio_job_id: Optional job ID for audio analysis

    Returns:
        CreateAnswer: Complete analysis result
    """
#     from rq.job import Job

#     # If job IDs aren't provided, start the jobs
#     if not audio_job_id:
#         audio_job_id = start_audio_analysis_job(video_url)
#     if not facial_job_id:
#         facial_job_id = start_facial_analysis_job(video_url)

#     # Get the job results
#     audio_job = Job.fetch(audio_job_id, connection=get_redis_con())
#     facial_job = Job.fetch(facial_job_id, connection=get_redis_con())

#     audio_result = await_job_result(audio_job.id)
#     facial_result = await_job_result(facial_job.id)

#     # If either job failed, return error
#     if not audio_result or not facial_result:
#         error_msg = "Failed to get results from audio or facial analysis jobs"
#         logger.error(error_msg)
#         if not audio_result:
#             logger.error(f"Audio job failed: {audio_job_id}")
#         if not facial_result:
#             logger.error(f"Facial job failed: {facial_job_id}")
#         raise ValueError(error_msg)
#     # Process the text structure
#     text_answer: TextStructureResult = score_text_structure(audio_result)

#     # Create timeline
#     timeline: List[TimelineStructure] = av_timeline_resolution(
#         audio_result.clip_length_seconds,
#         facial_result,
#         audio_result.sentiment_analysis,
#     )

#     # Calculate facial statistics
#     facial_stats, top_stat, second_stat, third_stat = (
#         calculate_top_three_facial_with_count(facial_result)
#     )

#     # Calculate Big Five scores
#     bigFive: BigFiveScoreResult = score_bigFive(audio_result, facial_stats, text_answer)

#     # Generate competency feedback
#     competency_feedback: OverallCompetencyFeedback = generate_competency_feedback(
#         facial_result, audio_result, text_answer
#     )

#     # Create facial statistics
#     facial_statistics = FacialStatistics(
#         topThreeEmotions=facial_stats,
#         frequencyOfTopEmotion=top_stat,
#         frequencyOfSecondEmotion=second_stat,
#         frequencyOfThirdEmotion=third_stat,
#     )

#     # Build evaluation result
#     evaluation = CreateAnswerEvaluation(
#         timeline=timeline,
#         isStructured=text_answer.binary_prediction,
#         predictionScore=text_answer.prediction_score,
#         facialStatistics=facial_statistics,
#         overallFacialEmotion=facial_stats[0] if facial_stats else "neutral",
#         overallSentiment=calculate_overall_audio_sentiment(audio_result),
#         topFiveKeywords=grab_top_five_keywords(audio_result),
#         transcript=text_answer.output_text,
#         bigFive=bigFive,
#         competencyFeedback=competency_feedback,
#     )

#     # Calculate aggregate score
#     evaluation.aggregateScore = compute_aggregate_score(evaluation)

#     # Return final result
#     return CreateAnswer(evaluation=evaluation)
