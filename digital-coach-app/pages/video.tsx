import { useState, useEffect, useRef } from "react";
import Card from "@App/components/atoms/Card";
import AuthGuard from "@App/lib/auth/AuthGuard";
import { useReactMediaRecorder } from "react-media-recorder";
import StorageService from "@App/lib/storage/StorageService";
import { v4 as uuidv4 } from "uuid";
import styles from "@App/styles/VideoPage.module.scss";
import axios from "axios";
import SelectQuestionSetCard from "@App/components/organisms/SelectQuestionSetCard";
import CircularProgressWithLabel from "@App/components/organisms/CircularProgressWithLabel";
import InterviewService from "@App/lib/interview/InterviewService";
import useAuthContext from "@App/lib/auth/AuthContext";
import { IBaseInterview } from "@App/lib/interview/models";

export default function VideoPage() {
  const { currentUser } = useAuthContext();
  const [isLocked, setIsLocked] = useState<any>(false);
  const [questions, setQuestions] = useState<any[]>([]);
  const [showQuestions, setShowQuestions] = useState<any>(true);
  const [wasRecording, setWasRecording] = useState<any>(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { status, startRecording, stopRecording, mediaBlobUrl, previewStream } =
    useReactMediaRecorder({ video: true });

  const [aggregateScore, setAggregateScore] = useState(0);
  const [jobId, setJobId] = useState("");
  const [feedback, setFeedback] = useState<any>([]);
  const [bigFive, setBigFive] = useState<any>({});

  const saveRecording = async () => {
    const getFile = async () => {
      const url = mediaBlobUrl ? mediaBlobUrl : "";
      let blob = await fetch(url).then((res) => res.blob());
      // const blob = new Blob([data as BlobPart], {
      // type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      // });
      // const blobPart = new Blob([blob as BlobPart]);

      return new File([blob], "video.mp4");
    };
    const file = await getFile();

    const url = (await StorageService.uploadAnswerVideo(file, uuidv4())) as any;
    const dlURL = await StorageService.getDownloadUrlFromVideoUrlRef(
      "gs://" + url.ref._location.bucket + "/" + url.ref._location.path,
    );

    console.log("THE URL:", dlURL);

    console.log("Predicting...");
    try {
      const response = await axios.post(
        "http://localhost:8000/api/create_answer/",
        {
          video_url: dlURL,
        },
      );
      console.log(response.data);
      setJobId(response.data.job_id);
    } catch (e) {
      console.log("Came up with error", e);
    }
  };

  const getResults = async () => {
    try {
      console.log(jobId);
      const response = await axios.get(
        "http://localhost:8000/api/create_answer/" + jobId + "/result",
      );
      console.log(response.data);
      setAggregateScore(response.data.evaluation.aggregateScore);
    } catch (e) {}
  };
  useEffect(() => {
    if (videoRef.current && previewStream) {
      videoRef.current.srcObject = previewStream;
    }
  }, [previewStream]);

  return (
    <AuthGuard>
      <div>
        <p className={styles.thing}>{status}</p>
        <div className={styles.videoBox}>
          <video src={mediaBlobUrl!} controls />
          <video ref={videoRef} controls autoPlay />
        </div>
        <div className={styles.buttonBox}>
          <button
            onClick={() => {
              setIsLocked(true);
              setWasRecording(true);
              startRecording();
            }}
          >
            Start Recording
          </button>
          <button
            onClick={() => {
              setIsLocked(false);
              if (wasRecording) {
                setQuestions([]);
                setShowQuestions(false);
                setWasRecording(false);
              }
              stopRecording();
            }}
          >
            Stop Recording
          </button>
          {mediaBlobUrl && (
            <button onClick={saveRecording}>Save Recording</button>
          )}
          <button onClick={getResults}>Get Results</button>
          <p>Most Recent Score: </p>
          {aggregateScore !== 0 && (
            <CircularProgressWithLabel value={aggregateScore} />
          )}
        </div>
      </div>
      <SelectQuestionSetCard
        isLocked={isLocked}
        setIsLocked={setIsLocked}
        questions={questions}
        setQuestions={setQuestions}
        showQuestions={showQuestions}
        setShowQuestions={setShowQuestions}
      />
      {feedback.length !== 0 && Object.keys(bigFive).length !== 0 && (
        <div>
          <Card title="Big Five Score">
            <p>Openness Score: {bigFive.o}</p>
            <p>Conscientiousness Score: {bigFive.c}</p>
            <p>Extraversion Score: {bigFive.e}</p>
            <p>Agreeableness Score: {bigFive.a}</p>
            <p>Neuroticism Score: {bigFive.n}</p>
          </Card>
          <Card title="Big Five Feedback">
            {feedback.map((thisFeedback: string) => {
              return <p>{thisFeedback}</p>;
            })}
          </Card>
        </div>
      )}
    </AuthGuard>
  );
}
