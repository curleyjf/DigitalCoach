import { useQuery } from "@tanstack/react-query";
import InterviewQuestionService from "../interviewQuestion/InterviewQuestionService";
import InterviewService from "./InterviewService";



/**
 * It fetches all interviews for a user, then for each interview, it fetches all questions for that
 * interview, then it checks if each question has been answered, and if so, it calculates a completion
 * percentage for that interview
 * @param {string} [userId] - string - the user id of the user to fetch the interviews for
 * @returns An array of objects with the following properties:
 * interviewId: string;
 * interviewName: string;
 * date: Date;
 * completionPct: number;
 */
export default function useResumeInterviewQuery(userId?: string) {
  return useQuery(
    ["resumeUserInterviews"],
    async () => {
      const interviews = await InterviewService.fetchUserInterviews(userId!);

      const interviewLookup = interviews.docs.map(async (interview) => {
        const interviewData =
          await InterviewQuestionService.getInterviewQuestions(interview.ref);

        const interviewQuestions = interviewData.docs;

        const completed = interviewQuestions.map(
          (interview) => interview.data().answeredAt !== null
        );
        const completionPct =
          completed.filter((item) => item).length / completed.length;
        if (completionPct === 1) {
          return null;
        }
        return {
          interviewId: interview.id,
          interviewName: interview.data().title,
          date: interview.data().createdAt.toDate(),
          completionPct,
        };
      });

      const incompleteInterviews = (await Promise.all(interviewLookup)).filter(
        (
          item
        ): item is {
          interviewId: string;
          interviewName: string;
          date: Date;
          completionPct: number;
        } => item !== null || item !== undefined
      );

      return incompleteInterviews;
    },
    {
      enabled: !!userId,
    }
  );
}
