import { useQuery } from "@tanstack/react-query";
import InterviewQuestionService from "../interviewQuestion/InterviewQuestionService";
import InterviewService from "./InterviewService";

/**
 * It returns a list of interviews for a given user, and for each interview, it returns the average
 * score and completion percentage.
 * 
 * @param {string | undefined} userId - string | undefined
 * @returns An array of objects.
 */
export default function usePastInterviewQuery(userId: string | undefined) {
  return useQuery(
    ["pastUserInterviews"],
    async () => {
      const interviews = await InterviewService.fetchUserInterviews(userId!);
      const interviewLookup = interviews.docs.map(async (interview) => {
        const interviewData =
          await InterviewQuestionService.getInterviewQuestions(interview.ref);

        const interviewQuestions = interviewData.docs;
        const scores = interviewQuestions
          .map((interview) => interview.data().score)
          .filter(
            (score): score is number => score !== undefined && score !== null
          );
        const averageScore =
          scores.reduce((acc, score) => acc + score, 0) / scores.length;
        const completed = interviewQuestions.map(
          (interview) => interview.data().answeredAt !== null
        );
        const completionPct =
          completed.filter((item) => item).length / completed.length;
        return {
          interviewId: interview.id,
          interviewName: interview.data().title,
          date: interview.data().createdAt.toDate(),
          averageScore,
          completionPct,
        };
      });
      return Promise.all(interviewLookup);
    },
    {
      enabled: !!userId,
    }
  );
}
