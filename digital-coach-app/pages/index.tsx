import type { NextPage } from "next";
import { useState, useEffect } from "react";
import useAuthContext from "@App/lib/auth/AuthContext";
import AuthGuard from "@App/lib/auth/AuthGuard";
import styles from "@App/styles/Home.module.scss";
import Card from "@App/components/atoms/Card";
import IssuesChart from "@App/components/molecules/IssuesChart";
import ScoreChart from "@App/components/molecules/ScoreChart";
import PracticeCalendar from "@App/components/molecules/PracticeCalendar";
import useGetFeaturedQuestionSets from "@App/lib/questionSets/useGetFeaturedQuestionSets";
import Link from "next/link";
import useGetUserAverageScore from "@App/lib/interviewQuestion/useGetUserAverageScore";
import useFetchUserInterviews from "@App/lib/interview/useFetchUserInterviews";
import useGetAnswersByUserId from "@App/lib/answer/useGetAnswerByUserId";
import seed from "@App/pages/api/seed";

const Home: NextPage = () => {
  const { currentUser } = useAuthContext();

  const {
    data: questionSets,
    isLoading,
    isFetching,
  } = useGetFeaturedQuestionSets();
  console.log(questionSets, isLoading, isFetching);

  const {
    data: answerData,
    isLoading: isAnswerLoading,
    isFetching: isAnswerFetching,
  } = useGetAnswersByUserId(currentUser?.id);

  const {
    data: averageScore,
    isLoading: isLoadingAverageScore,
    isFetching: isFetchingAverageScore,
  } = useGetUserAverageScore(currentUser?.id);

  const [tip, setTips] = useState("");

  useEffect(() => {
    const tips = [
      "Practice active listening during the interview. Pay attention to the questions asked and respond thoughtfully.",
      "Research common behavioral interview questions and prepare STAR (Situation, Task, Action, Result) stories to showcase your skills and experiences.",
      "Arrive early for the interview to allow time for unexpected delays and to demonstrate your punctuality.",
      "Turn off your phone or set it to silent mode before the interview to avoid distractions.",
      "Maintain good body language throughout the interview. Sit up straight, make eye contact, and smile to convey confidence.",
      "Research the salary range for similar positions in your industry and be prepared to discuss salary expectations if asked.",
      "Practice good hygiene and grooming before the interview. A neat appearance contributes to a positive first impression.",
      "Review the job description and customize your answers to align with the requirements of the role.",
      "Stay positive and enthusiastic during the interview. A positive attitude can leave a lasting impression on the interviewer.",
      "Start by researching the company and your interviewer. Understanding key information about the company you’re interviewing with can help you go into your interview with confidence.",
      "Practice answering common interview questions to build your confidence and improve your responses during the actual interview.",
      "Dress appropriately for your interview. Your attire should be professional and suitable for the company culture.",
      "Prepare questions to ask the interviewer. This shows your interest in the position and company and can help you gather important information.",
      "Stay calm and composed during the interview. Take a deep breath if you feel nervous and focus on articulating your thoughts clearly.",
      "Highlight your achievements and relevant experiences during the interview. Use specific examples to demonstrate your skills and capabilities.",
      "Follow up with a thank-you email after the interview. Express your gratitude for the opportunity and reiterate your interest in the position.",
    ];
    const randInd = Math.floor(Math.random() * tips.length);
    setTips(tips[randInd]);
  }, []);

  if (isLoading || isFetching) return <div>Loading...</div>;

  const mockIssuesData = [
    {
      skill: "No Eye Contact",
      value: 0.9,
    },
    {
      skill: "Filler Word",
      value: 0.75,
    },
    {
      skill: "Long Pause",
      value: 0.65,
    },
    {
      skill: "Voice Not Clear",
      value: 0.6,
    },
    {
      skill: "Off Topic",
      value: 0.4,
    },
  ];
  const events =
    answerData?.docs.map((answer) => {
      return {
        start: answer.data().createdAt.toDate().toISOString(),
        end: answer.data().createdAt.toDate().toISOString(),
      };
    }) || [];

  return (
    <AuthGuard>
      <div className={styles.Home}>
        <h1>Welcome back, {currentUser?.data()?.name}!</h1>
        <h2>Dashboard</h2>
        <div className={styles.cards}>
          <Card title={"Quick Start Interviews"} multiline>
            <ul>
              {questionSets?.docs.map((questionSet) => (
                <li key={questionSet.id}>
                  <Link href="/">{questionSet.data().title}</Link>
                  <span>→</span>
                </li>
              ))}
            </ul>
          </Card>
          <Card title={"Your Random Interview Tip!"} multiline>
            <div className={styles.tipoftheday}>
              <p>{tip}</p>
            </div>
          </Card>
          <Card title={"Recent Recordings"} multiline>
            <h4>You have not recorded an interview yet!</h4>
          </Card>
          <Card multiline>
            <div className={styles.calendarWrapper}>
              <PracticeCalendar events={events} />
            </div>
          </Card>
          <Card title={"Most Common Flags"} multiline>
            <div className={styles.issuesChartWrapper}>
              <IssuesChart chartData={mockIssuesData} />
            </div>
            <h2>Average Score: {Math.round(averageScore * 100)}%</h2>
          </Card>
        </div>

        {/*
        <span>id: {currentUser?.id}</span>
        <span>email: {currentUser?.email}</span>
        <span>name: {currentUser?.name}</span>
        <span>concentration: {currentUser?.concentration}</span>
        <span>proficiency: {currentUser?.proficiency}</span>*/}
      </div>
    </AuthGuard>
  );
};

export default Home;
