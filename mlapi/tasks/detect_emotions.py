from schemas.create_answer import (
    EmotionDetectionResult,
    EmotionTotals,
    EmotionTimelines,
)
import cv2
from deepface import DeepFace
from collections import defaultdict
from tqdm import tqdm
import time
from utils.logger_config import get_logger
from rq.decorators import job
from redisStore.myconnection import get_redis_con
import nltk

logger = get_logger(__name__)

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")
nltk.download("wordnet")


@job("high", connection=get_redis_con())
def detect_emotions(video_url: str, sample_rate=30) -> EmotionDetectionResult:
    """
    Detect emotions in a video using DeepFace

    Args:
        video_url: Path or URL to the video file
        sample_rate: Process every Nth frame (default: 30)

    Returns:
        EmotionDetectionResult: Standardized emotion detection results
    """
    # Initialize result with default values
    result = EmotionDetectionResult(
        total_frames=0,
        frame_inference_rate=sample_rate,
        emotion_sums=EmotionTotals(),
        timeline=EmotionTimelines(),
        clip_length_seconds=0.0,
        errors=None,
        avg_inference_time=0.0,
    )

    try:
        # Open the video file
        logger.info(f"Opening video file: {video_url}")
        video = cv2.VideoCapture(video_url)
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_url}")

        # Get video properties
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        result.clip_length_seconds = duration

        logger.info(f"Video duration: {duration:.2f} seconds ({frame_count} frames)")

        # Initialize variables for frame processing
        processed_frames = 0
        frame_idx = 0
        total_inference_time = 0.0

        # Initialize timeline arrays with zeros for each frame we'll process
        frames_to_process = frame_count // sample_rate + 1

        # Process the video
        logger.info(f"Processing video with sample rate: {sample_rate}")
        with tqdm(total=frames_to_process, desc="Processing frames") as pbar:
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break

                # Process every Nth frame based on sample_rate
                if frame_idx % sample_rate == 0:
                    timeline_idx = processed_frames

                    try:
                        # Measure inference time
                        start_time = time.time()

                        # Use DeepFace for emotion analysis
                        analysis = DeepFace.analyze(
                            img_path=frame,
                            actions=["emotion"],
                            enforce_detection=False,  # Don't error if no face is detected
                            detector_backend="opencv",  # Faster for CPU
                        )

                        end_time = time.time()
                        inference_time = end_time - start_time
                        total_inference_time += inference_time

                        # DeepFace can return a list or a dict depending on number of faces
                        if isinstance(analysis, list):
                            faces_analysis = analysis
                        else:
                            faces_analysis = [analysis]

                        # If faces were detected
                        if len(faces_analysis) > 0:
                            # Process emotions for all faces in the frame
                            frame_emotions = defaultdict(float)

                            for face_analysis in faces_analysis:
                                emotion_scores = face_analysis["emotion"]

                                # Process each emotion
                                for emotion, score in emotion_scores.items():
                                    # Convert to lowercase to match our keys
                                    emotion_key = emotion.lower()
                                    if emotion_key in result.emotion_sums.dict():
                                        frame_emotions[emotion_key] += (
                                            score / 100.0
                                        )  # DeepFace returns percentages

                            # Average emotions across all faces
                            num_faces = len(faces_analysis)
                            for emotion, score in frame_emotions.items():
                                # Add to the total sum
                                setattr(
                                    result.emotion_sums,
                                    emotion,
                                    getattr(result.emotion_sums, emotion)
                                    + score / num_faces,
                                )

                                # Add to the timeline for this frame
                                # Extend the timeline list as needed
                                timeline = getattr(result.timeline, emotion)
                                while len(timeline) <= timeline_idx:
                                    timeline.append(0.0)
                                timeline[timeline_idx] = score / num_faces
                                setattr(result.timeline, emotion, timeline)

                    except Exception as e:
                        logger.error(f"Error processing frame {frame_idx}: {str(e)}")
                        # If there's an error, just continue with the next frame

                    processed_frames += 1
                    pbar.update(1)

                frame_idx += 1

        # Update the result with total processed frames
        result.total_frames = processed_frames

        # Calculate average inference time
        if processed_frames > 0:
            result.avg_inference_time = total_inference_time / processed_frames

        # Release video capture
        video.release()

        logger.info(f"Video processing completed: {processed_frames} frames processed")

    except Exception as e:
        error_msg = f"Error processing video: {str(e)}"
        logger.error(error_msg)
        result.errors = error_msg

    return result
