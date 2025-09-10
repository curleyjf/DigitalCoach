import { useState, useEffect, useRef } from "react";
import Transcript from "@App/components/organisms/Transcript";
import AuthGuard from "@App/lib/auth/AuthGuard";
import { useReactMediaRecorder } from "react-media-recorder";
import StorageService from "@App/lib/storage/StorageService";
import { v4 as uuidv4 } from "uuid";
import styles from "@App/styles/NaturalConversationPage.module.scss";
import axios from "axios";
import InteractiveAvatar from "@App/components/organisms/InteractiveAvatar";

interface Message {
  role: "user" | "interviewer";
  text: string;
  timestamp: string;
}

export default function NaturalConversationPage() {
  const avatarRef = useRef<{
    startSession: () => void;
    endSession: () => void;
    handleInterrupt: () => void;
  } | null>(null);

  const [wasRecording, setWasRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { startRecording, stopRecording, mediaBlobUrl, previewStream } =
    useReactMediaRecorder({ video: true });

  // Callback to add a new user message.
  const handleUserTranscript = (userTranscript: string) => {
    const newMessage: Message = {
      role: "user",
      text: userTranscript,
      timestamp: new Date().toLocaleString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  // Callback to add a new interviewer (HeyGen API) message.
  const handleInterviewerTranscript = (interviewerTranscript: string) => {
    const newMessage: Message = {
      role: "interviewer",
      text: interviewerTranscript,
      timestamp: new Date().toLocaleString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleStartInterview = async () => {
    if (wasRecording) {
      stopRecording();
      await avatarRef.current?.endSession();
      setWasRecording(false);
    } else {
      setWasRecording(true);
      await avatarRef.current?.startSession();
      startRecording();
    }
  };

  const handleInterruptAvatar = async () => {
    await avatarRef.current?.handleInterrupt();
  };

  const waitForJobResult = async (
    jobId: string,
    retries = 10,
    delay = 3000
  ) => {
    for (let i = 0; i < retries; i++) {
      const statusRes = await axios.get(
        `http://localhost:8000/api/create_answer/${jobId}`
      );

      if (statusRes.data.status === "completed") {
        return axios.get(
          `http://localhost:8000/api/create_answer/${jobId}/result`
        );
      }

      await new Promise((res) => setTimeout(res, delay));
    }
    throw new Error("Job did not complete in time.");
  };

  // Optional: This function is still available if you need to manually fetch a response.
  const getResponse = async () => {
    try {
      const getFile = async () => {
        const url = mediaBlobUrl || "/output.mp4";
        let blob = await fetch(url).then((res) => res.blob());
        return new File([blob], "video.mp4");
      };
      const file = await getFile();

      const url = (await StorageService.uploadAnswerVideo(
        file,
        uuidv4()
      )) as any;
      const dlURL = await StorageService.getDownloadUrlFromVideoUrlRef(
        "gs://" + url.ref._location.bucket + "/" + url.ref._location.path
      );
      console.log(dlURL);

      const sentResponse = await axios.post(
        "http://localhost:8000/api/create_answer/",
        {
          video_url: dlURL,
        }
      );
      const jobId = sentResponse.data.job_id;

      const jobIdResponse = await waitForJobResult(jobId);

      console.log(jobIdResponse);
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while processing the recording.");
    }
  };

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.srcObject = previewStream || null;
    }
  }, [previewStream]);

  return (
    <AuthGuard>
      <div className={styles.pageContainer}>
        <div className={styles.videoAndButtonContainer}>
          <div className={styles.videoContainer}>
            <div className={styles.videoBox}>
              <div className={styles.userVideoContainer}>
                <video
                  ref={videoRef}
                  controls
                  autoPlay
                  className={styles.userVideo}
                />
              </div>
              {/* Pass both transcript callbacks to InteractiveAvatar */}
              <InteractiveAvatar
                ref={avatarRef}
                onTranscriptChange={handleUserTranscript}
                onInterviewerTranscriptChange={handleInterviewerTranscript}
              />
              <div className={styles.buttonBox}>
                <button
                  className={styles.recordButton}
                  onClick={handleStartInterview}
                >
                  {wasRecording ? "Stop Interview" : "Start Interview"}
                </button>
                <button
                  className={styles.saveButton}
                  onClick={handleInterruptAvatar}
                >
                  Interrupt Task
                </button>
                <button className={styles.saveButton} onClick={getResponse}>
                  GetResponse
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.transcriptContainer}>
          <Transcript title="Transcript">
            {messages.length > 0 ? (
              messages.map((message, index) => (
                <div key={index}>
                  <p>
                    <strong>
                      [{message.timestamp}]{" "}
                      {message.role === "user" ? "User:" : "Interviewer:"}
                    </strong>
                  </p>
                  <p>{message.text}</p>
                </div>
              ))
            ) : (
              <p>No transcript available.</p>
            )}
          </Transcript>
        </div>
      </div>
    </AuthGuard>
  );
}
