import { useState, useEffect, useRef } from "react";
import Card from "@App/components/atoms/Card";
import AuthGuard from "@App/lib/auth/AuthGuard";
import { useReactMediaRecorder } from "react-media-recorder";
import StorageService from "@App/lib/storage/StorageService";
import { v4 as uuidv4 } from "uuid";
import styles from "@App/styles/StorytellingPage.module.scss";
import axios from "axios";
import SelectQuestionSetCard from "@App/components/organisms/SelectQuestionSetCard";
import CircularProgressWithLabel from "@App/components/organisms/CircularProgressWithLabel";
import InterviewService from "@App/lib/interview/InterviewService";
import useAuthContext from "@App/lib/auth/AuthContext";
import { IBaseInterview } from "@App/lib/interview/models";

export default function StorytellingPage() {
  const { currentUser } = useAuthContext();
  const [isLocked, setIsLocked] = useState<any>(false);
  const [showQuestions, setShowQuestions] = useState<boolean>(false);
  const [showScenarios, setShowScenarios] = useState<boolean>(false);
  const [questions, setQuestions] = useState<any[]>([]);
  const [selectedQuestions, setSelectedQuestions] = useState<string[]>([]);
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [wasRecording, setWasRecording] = useState<any>(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { status, startRecording, stopRecording, mediaBlobUrl, previewStream } =
    useReactMediaRecorder({ video: true });

  const [aggregateScore, setAggregateScore] = useState(0);
  const [jobId, setJobId] = useState("");
  const [transcript, setTranscript] = useState("");
  const [feedback, setFeedback] = useState<any>([]);
  const [bigFive, setBigFive] = useState<any>({});
  const [starData, setStarData] = useState<any>([]);
  const [starFeedback, setStarFeedback] = useState<any>([]);
  const [fulfilledStarCheck, setFulfilledStarCheck] = useState<boolean>(false);

  const [prevFeedback, setPrevFeedback] = useState<any>({});
  const [prevStarFeedback, setPrevStarFeedback] = useState<any>({});
  const [prevBigFive, setPrevBigFive] = useState<any>({});
  const [prevStar, setPrevStar] = useState<boolean>(false);

  const allSelectedItems = [...selectedQuestions, ...selectedScenarios];
  const canAddItem = allSelectedItems.length < 10;

  const sampleQuestions = [
    "Can you think of a time when you had to take care of someone? How did it affect you?",
    "Tell me about a time when you accomplished something you’re really proud of, even if it was small.",
    "What was your most difficult class and what did you do to get through it?",
    "Tell me about a time when you took on a leadership role in a club, team, or school activity. What did you accomplish?",
    "Share a time when you had to meet a tight deadline. How did you ensure success?",
    "Can you recall a moment when you received constructive criticism? How did you respond to it?",
    "Tell me about a time when you successfully managed multiple priorities. How did you organize your time?",
    "Can you provide an example of when you worked on a project with little guidance? How did you manage it?",
    "Tell me about a time when you had to explain something complicated to someone. How did you make it clear and understandable?",
    "Describe a time when you worked on a group project in school. How did you contribute, and what was the result?",
    "Can you describe a time when you resolved a misunderstanding or prevented a conflict? How did you approach the situation?",
    "Is there a situation you think you could’ve handled better or differently?",
    "Describe a situation where you had to persuade others to see things your way. How did you achieve this?",
    "Think of a time when you had to make a quick decision under pressure. What happened, and how did you handle it?",
    "Tell me about a time when you faced a challenge in pursuing a hobby or activity you enjoy. How did you overcome it?",
    "Describe a time where you made something for someone else? Why? What was their reaction?",
    "What was the first job you ever had? Do you remember how you adapted and learned the ropes?",
    "Give me an example of a time when you came up with a creative solution to a problem at work. What happened?",
    "Give me an example of a time you made a mistake at work.",
    // Add more questions here...
  ];

  const sampleScenarios = [
    "You’re struggling to understand a concept in class and need to prepare for an important exam. What steps would you take to overcome this challenge?",
    "Your team is assigned a project with minimal guidance from leadership. How would you take initiative to organize the team and ensure the project is completed successfully?",
    "You notice a friend is being excluded from group activities or conversations. What would you do to include them and support them?",
    "You’re working on a team project, and a key team member suddenly quits or becomes unavailable right before a deadline. How would you handle their responsibilities?",
    "You’re tasked with making a group decision, but everyone has different opinions. How would you work to find a solution that satisfies most people?",
    "You had to prepare for a presentation or speech for a small group, but public speaking makes you nervous. How did you overcome your nerves and deliver the presentation?",
    // Add more scenarios here...
  ];

  const selectQuestion = (question: string) => {
    if (canAddItem && !selectedQuestions.includes(question)) {
      setSelectedQuestions((prev) => [...prev, question]);
    }
  };

  const selectScenario = (scenario: string) => {
    if (canAddItem && !selectedScenarios.includes(scenario)) {
      setSelectedScenarios((prev) => [...prev, scenario]);
    }
  };

  const toggleQuestionsVisibility = () => {
    setShowQuestions((prev) => !prev);
  };

  const toggleScenariosVisibility = () => {
    setShowScenarios((prev) => !prev);
  };

  const cycleItem = (direction: "next" | "prev") => {
    if (direction === "next") {
      setCurrentIndex(
        (prev) =>
          (prev + 1) % (selectedQuestions.length + selectedScenarios.length)
      );
    } else {
      setCurrentIndex(
        (prev) =>
          (prev - 1 + (selectedQuestions.length + selectedScenarios.length)) %
          (selectedQuestions.length + selectedScenarios.length)
      );
    }
  };

  const resetItems = () => {
    setSelectedQuestions([]);
    setSelectedScenarios([]);
    setCurrentIndex(0);
  };

  const saveRecording = async () => {
    const getFile = async () => {
      const url = mediaBlobUrl || "/output.mp4";
      let blob = await fetch(url).then((res) => res.blob());
      return new File([blob], "video.mp4");
    };
    const file = await getFile();

    const url = (await StorageService.uploadAnswerVideo(file, uuidv4())) as any;
    const dlURL = await StorageService.getDownloadUrlFromVideoUrlRef(
      "gs://" + url.ref._location.bucket + "/" + url.ref._location.path
    );
    try {
      const response = await axios.post(
        "http://localhost:8000/api/create_answer/",
        {
          video_url: dlURL,
        }
      );
      console.log(response);
      setJobId(response.data.job_id);
    } catch (e) {
      console.log(e);
    }
  };

  const getResults = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/create_answer/${jobId}`
      );
      if (response.data.status === "completed") {
        const jobResponse = await axios.get(
          `http://localhost:8000/api/create_answer/${jobId}/result`
        );
        console.log(jobResponse);
        setAggregateScore(jobResponse.data.evaluation.aggregateScore);
        setBigFive(jobResponse.data.evaluation.bigFive);
        setTranscript(jobResponse.data.evaluation.transcript);
      } else {
        alert(
          "The results are not ready yet. Please try again in a minute or so"
        );
      }
    } catch (e) {}
  };

  const sendAudio = async () => {
    const getFile = async () => {
      const url = mediaBlobUrl || "/output.mp4";
      let blob = await fetch(url).then((res) => res.blob());
      return new File([blob], "video.mp4");
    };
    const file = await getFile();

    const url = (await StorageService.uploadAnswerVideo(file, uuidv4())) as any;
    const dlURL = await StorageService.getDownloadUrlFromVideoUrlRef(
      "gs://" + url.ref._location.bucket + "/" + url.ref._location.path
    );
    try {
      const response = await axios.post(
        "http://localhost:8000/api/audio_analysis/",
        {
          video_url: dlURL,
        }
      );
      console.log(response);
      setJobId(response.data.job_id);
    } catch (e) {
      console.log(e);
    }
  };
  const getAudioResults = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/audio_analysis/${jobId}`
      );
      if (response.data.status === "completed") {
        const jobResponse = await axios.get(
          `http://localhost:8000/api/audio_analysis/${jobId}/result`
        );
        console.log(jobResponse);
      } else {
        alert(
          "The results are not ready yet. Please try again in a minute or so"
        );
      }
    } catch (e) {}
  };
  const sendStarTranscript = async () => {
    try {
      const starResponse = await axios.post(
        "http://localhost:8000/api/star_feedback/analyze",
        {
          text: transcript,
        }
      );
      setJobId(starResponse.data.job_id);
    } catch (e) {}
  };

  const getStartFeedBack = async () => {
    try {
      const starJobResponse = await axios.get(
        `http://localhost:8000/api/star_feedback/results/${jobId}`
      );
      setStarData(starJobResponse.data);

      let tempStarFeedback = [];
      if (starData.percentages.situation < 15) {
        tempStarFeedback.push(
          "You need to work on the Situation category. Try to focus on the context of the Situation and the circumstances that lead you to the task. The expected percentage for the Result category is 10% of your total response."
        );
      }
      if (starData.percentages.task < 10) {
        tempStarFeedback.push(
          "You need to work on the Task category. Try to focus on the task itself. The expected percentage for the Task category is 10% of your total response."
        );
      }
      if (starData.percentages.action < 60) {
        tempStarFeedback.push(
          "You need to work on the Action category. The Action category is the most important part of the STAR method. Try to focus on what you did and how you did it. The expected percentage for the Action category is 60% of your total response."
        );
      }
      if (starData.percentages.result < 15) {
        tempStarFeedback.push(
          "You need to work on the Result category. Try to focus on outcomes related to your task or action. The expected percentage for the Result category is 15% of your total response."
        );
      }
      setStarFeedback(tempStarFeedback);
      console.log(tempStarFeedback);

      setFulfilledStarCheck(starData.fulfilledStar);

      setPrevFeedback(feedback);
      setPrevStarFeedback(starFeedback);
      setPrevBigFive(bigFive);
      setPrevStar(fulfilledStarCheck);
      InterviewService.create(
        currentUser!.id,
        { title: "Test" } as IBaseInterview,
        response.data.result.evaluation
      );
      // Now need to give feedback based on Big Five Score
      let userFeedback = [];
      // Openness feedback
      if (response.data.result.evaluation.bigFive.o < -3) {
        userFeedback.push(
          "With an Openness score less that -3, you are more likely to stick to your routines, avoid change and follow a traditional thought process."
        );
      } else if (
        -3 <= response.data.result.evaluation.bigFive.o &&
        response.data.result.evaluation.bigFive.o <= 3
      ) {
        userFeedback.push(
          "With an Openness score between -3 and 3, you are somewhat open to new experiences and creative, but you still enjoy some structure and consistency."
        );
      } else if (response.data.result.evaluation.bigFive.o > 3) {
        userFeedback.push(
          "With an Openness score greater that 3, you likely enjoy trying new things, are creative and imaginative and can easily think about problems in different ways."
        );
      }

      // Conscientiousness feedback
      if (response.data.result.evaluation.bigFive.c < -3) {
        userFeedback.push(
          "With a Conscientiousness score less that -3, you are likely less organized and more willing to finish tasks at the last minute."
        );
      } else if (
        -3 <= response.data.result.evaluation.bigFive.c &&
        response.data.result.evaluation.bigFive.c <= 3
      ) {
        userFeedback.push(
          "With a Conscientiousness score between -3 and 3, you accept some level of order, but also like doing some things at your own pace."
        );
      } else if (response.data.result.evaluation.bigFive.c > 3) {
        userFeedback.push(
          "With a Conscientiousness score greater that 3, you are always prepared, keep things in order and are very goal driven."
        );
      }

      // Extraversion feedback
      if (response.data.result.evaluation.bigFive.e < -3) {
        userFeedback.push(
          "With an Extraversion score less that -3, you may struggle to socialize and prefer keeping to yourself."
        );
      } else if (
        -3 <= response.data.result.evaluation.bigFive.e &&
        response.data.result.evaluation.bigFive.e <= 3
      ) {
        userFeedback.push(
          "With an Extraversion score between -3 and 3, you enjoy your personal time but also like the occasional exciting activity or large gathering."
        );
      } else if (response.data.result.evaluation.bigFive.e > 3) {
        userFeedback.push(
          "With an Extraversion score greater that 3, you live for excitement and like to be around others. You recharge with others rather than without them."
        );
      }

      // Agreeableness feedback
      if (response.data.result.evaluation.bigFive.a < -3) {
        userFeedback.push(
          "With an Agreeableness score less that -3, you likely focus more on yourself and care less about how others feel about you."
        );
      } else if (
        -3 <= response.data.result.evaluation.bigFive.a &&
        response.data.result.evaluation.bigFive.a <= 3
      ) {
        userFeedback.push(
          "With an Agreeableness score between -3 and 3, you are willing to help others and care about them, but stil prioritize yourself"
        );
      } else if (response.data.result.evaluation.bigFive.a > 3) {
        userFeedback.push(
          "With an Agreeableness score greater that 3, you care about others, are always ready to help them and see the best in them"
        );
      }

      // Neuroticism feedback
      if (response.data.result.evaluation.bigFive.n < -3) {
        userFeedback.push(
          "With a Neuroticism score less that -3, you are able to remain calm even in high stress situations. You also remain optimistic and do not worry so much."
        );
      } else if (
        -3 <= response.data.result.evaluation.bigFive.n &&
        response.data.result.evaluation.bigFive.n <= 3
      ) {
        userFeedback.push(
          "With a Neuroticism score between -3 and 3, you have some confidence in yourself and can stay calm in somewhat stressful situations, but still carry self doubts."
        );
      } else if (response.data.result.evaluation.bigFive.n > 3) {
        userFeedback.push(
          "With a Neuroticism score greater that 3, you may be very insecure and get stressed out easily, and you tend to blame yourself when things go wrong."
        );
      }

      // Output the feedback on the screen for the user
      setFeedback(userFeedback);
      console.log(userFeedback);
    } catch (e) {}
  };
  const TestResponse = async () => {
    const getFile = async () => {
      const url = "/output.mp4";
      let blob = await fetch(url).then((res) => res.blob());
      return new File([blob], "video.mp4");
    };
    const file = await getFile();

    const url = (await StorageService.uploadAnswerVideo(file, uuidv4())) as any;
    const dlURL = await StorageService.getDownloadUrlFromVideoUrlRef(
      "gs://" + url.ref._location.bucket + "/" + url.ref._location.path
    );
    try {
      const response = await axios.post(
        "http://localhost:8000/api/create_answer/",
        {
          video_url: dlURL,
        }
      );
      console.log(response);
      setJobId(response.data.job_id);
    } catch (e) {
      console.log(e);
    }
  };

  const showPreviousResults = () => {
    setFeedback(prevFeedback);
    setStarFeedback(prevStarFeedback);
    setBigFive(prevBigFive);
    setFulfilledStarCheck(prevStar);
  };

  useEffect(() => {
    if (videoRef.current && previewStream) {
      videoRef.current.srcObject = previewStream;
    }
  }, [previewStream]);

  return (
    <AuthGuard>
      <div>
        {/* <p className={styles.thing}>{status}</p> */}
        <div className={styles.videoBox}>
          <video src={mediaBlobUrl!} controls />
          <video ref={videoRef} controls autoPlay />
        </div>
        <div className={styles.buttonBox}>
          <button
            className={styles.recordButton}
            onClick={() => {
              setIsLocked(true);
              setWasRecording(true);
              startRecording();
            }}
          >
            Start Recording
          </button>
          <button
            className={styles.recordButton}
            onClick={() => {
              setIsLocked(false);
              if (wasRecording) {
                setQuestions([]);
                setShowQuestions(false);
                setShowScenarios(false);
                setWasRecording(false);
              }
              stopRecording();
            }}
          >
            Stop Recording
          </button>
          {mediaBlobUrl && (
            <button className={styles.saveButton} onClick={saveRecording}>
              Save Recording
            </button>
          )}
          <button className={styles.resultButton} onClick={TestResponse}>
            Test Response
          </button>
          <button className={styles.resultButton} onClick={getResults}>
            Get Results
          </button>
          <button className={styles.resultButton} onClick={sendAudio}>
            Send Audio
          </button>
          <button className={styles.resultButton} onClick={getAudioResults}>
            Get Audio Results
          </button>
          <button className={styles.resultButton} onClick={sendStarTranscript}>
            Send Star
          </button>
          {/* Previou Results */}
          {prevFeedback.length > 0 && prevBigFive.length && (
            <button
              className={styles.resultButton}
              onClick={showPreviousResults}
            >
              Show Previous Results
            </button>
          )}
        </div>
      </div>
      {/* Selected Item Slideshow */}
      {allSelectedItems.length > 0 ? (
        <div className={styles.itemSlideshow}>
          <h3>{allSelectedItems[currentIndex]}</h3>
          <div className={styles.buttonContainer}>
            <button
              className={styles.prevButton}
              onClick={() => cycleItem("prev")}
            >
              Previous
            </button>
            <button
              className={styles.nextButton}
              onClick={() => cycleItem("next")}
            >
              Next
            </button>
          </div>
        </div>
      ) : (
        <p>No items selected yet</p>
      )}

      {/* Reset Button */}
      <div className={styles.buttonBox}>
        <button className={styles.resetButton} onClick={resetItems}>
          Reset Selections
        </button>
      </div>

      <div className={styles.browseSectionContainer}>
        {/* Browse Questions */}
        <div className={styles.browseSection}>
          <button
            className={styles.browseButton}
            onClick={toggleQuestionsVisibility}
          >
            {showQuestions ? "Hide Questions" : "Browse Questions"}
          </button>
          {showQuestions && (
            <div className={styles.questionList}>
              {sampleQuestions.map((question, index) => (
                <div key={index}>
                  <button
                    className={styles.questionButton}
                    disabled={selectedQuestions.includes(question)}
                    onClick={() => selectQuestion(question)}
                  >
                    {question}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Browse Scenarios */}
        <div className={styles.browseSection}>
          <button
            className={styles.browseButton}
            onClick={toggleScenariosVisibility}
          >
            {showScenarios ? "Hide Scenarios" : "Browse Scenarios"}
          </button>
          {showScenarios && (
            <div className={styles.scenarioList}>
              {sampleScenarios.map((scenario, index) => (
                <div key={index}>
                  <button
                    className={styles.questionButton}
                    disabled={selectedScenarios.includes(scenario)}
                    onClick={() => selectScenario(scenario)}
                  >
                    {scenario}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      {/* Display Score and Feedback */}
      {feedback.length !== 0 &&
        starFeedback.length !== 0 &&
        Object.keys(bigFive).length !== 0 && (
          <div>
            <Card title="Overall Score">
              {aggregateScore !== 0 && (
                <Card>
                  <div className={styles.scoreContainer}>
                    <CircularProgressWithLabel value={aggregateScore} />
                    <div className={styles.scoreMessage}>
                      {/* Conditionally show score message */}
                      {aggregateScore >= 90 && (
                        <p>Excellent! Keep up the great work!</p>
                      )}
                      {aggregateScore >= 70 && aggregateScore < 90 && (
                        <p>Good job! There's room for improvement.</p>
                      )}
                      {aggregateScore >= 50 && aggregateScore < 70 && (
                        <p>
                          Decent performance. Try to focus on areas of
                          improvement.
                        </p>
                      )}
                      {aggregateScore < 50 && (
                        <p>Needs improvement. Keep practicing!</p>
                      )}
                    </div>
                  </div>
                </Card>
              )}
              <Card title="Big Five Scores">
                <div className={styles.scoresBox}>
                  <p>Openness Score: {bigFive.o}</p>
                  <p>Conscientiousness Score: {bigFive.c}</p>
                  <p>Extraversion Score: {bigFive.e}</p>
                  <p>Agreeableness Score: {bigFive.a}</p>
                  <p>Neuroticism Score: {bigFive.n}</p>
                </div>
                {feedback.map((thisFeedback: string) => {
                  return <p>{thisFeedback}</p>;
                })}
              </Card>

              <Card title="STAR Feedback">
                <div className={styles.scoresBox}>
                  <p>STAR fulfillment: {fulfilledStarCheck ? "Yes" : "No"}</p>
                  <p>Situation: {starData.percentages.situation}%</p>
                  <p>Task: {starData.percentages.task}%</p>
                  <p>Action: {starData.percentages.action}%</p>
                  <p>Results: {starData.percentages.result}%</p>
                </div>
                {starFeedback.map((thisStarFeedback: string) => {
                  return <p>{thisStarFeedback}</p>;
                })}
              </Card>
            </Card>
          </div>
        )}
    </AuthGuard>
  );
}
