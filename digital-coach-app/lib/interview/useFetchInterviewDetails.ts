import { useQuery } from "@tanstack/react-query";
import AnswerService from "../answer/AnswerService";
import useAuthContext from "../auth/AuthContext";
import InterviewQuestionService from "../interviewQuestion/InterviewQuestionService";
import InterviewService from "./InterviewService";

/**
 * It fetches an interview, then fetches the interview questions, then fetches the answers for each
 * interview question.
 * @param {string} interviewId - string - The id of the interview to fetch
 * @returns An object with two properties: interview and questions.
 */
export default function useGetInterviewDetails(interviewId: string) {
  const { currentUser } = useAuthContext();

  const getInterviewDetails = async () => {
    const interview = await InterviewService.fetchInterview({
      userId: currentUser!.id,
      interviewId,
    });

    const interviewQuestions =
      await InterviewQuestionService.getInterviewQuestions(interview.ref);

    const questions = interviewQuestions.docs.map(
      async (interviewQuestionDoc) => {
        const answers = await AnswerService.getAnswers(
          interviewQuestionDoc.ref
        );

        return {
          ...interviewQuestionDoc,
          data: { answers, ...interviewQuestionDoc.data() },
        };
      }
    );

    return { interview, questions };
  };

  return useQuery(["interviewDetails", interviewId], getInterviewDetails, {
    enabled: !!currentUser,
  });
}
