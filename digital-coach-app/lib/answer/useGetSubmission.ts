import { useQuery } from "@tanstack/react-query";
import InterviewService from "../interview/InterviewService";
import InterviewQuestionService from "../interviewQuestion/InterviewQuestionService";
import StorageService from "../storage/StorageService";
import AnswerService from "./AnswerService";

/**
 * It fetches the interview, question, and submission data from Firestore, and then returns the
 * interview name, question name, video url, and evaluation.
 * </code>
 * @param {string} userId - string
 * @param {string} interviewId - string, questionId: string, userId: string
 * @param {string} questionId - string - the id of the question
 * @returns The useGetSubmission function is returning the useQuery hook.
 */
export default function useGetSubmission(userId: string, interviewId: string, questionId: string) {
  return useQuery(
    ["getSubmission"],
    async () => {
        const interview = await InterviewService.fetchInterview({userId, interviewId});
        const interviewData = interview.data();
        const question = await InterviewQuestionService.getInterviewQuestion(userId, interviewId, questionId);
        const questionData = question.data();
        const submission = await AnswerService.getSubmission(question.ref);
        if(!interviewData || !questionData || !submission) return null;
        const downloadVideoUrl = await StorageService.getDownloadUrlFromVideoUrlRef(submission.data().videoUrl);
        return {interviewName: interviewData.title, questionName: questionData.question, videoUrl: downloadVideoUrl, evaluation: submission.data().evaluation};
    },
    {
      enabled: !!userId && !!interviewId && !!questionId,
    }
  );
}
