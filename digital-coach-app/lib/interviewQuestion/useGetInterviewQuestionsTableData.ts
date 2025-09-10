import { useQuery } from "@tanstack/react-query";
import AnswerService from "../answer/AnswerService";
import InterviewQuestionService from "./InterviewQuestionService";
import {ref, getStorage} from 'firebase/storage'
import StorageService from "../storage/StorageService";



/**
 * It returns a list of objects that contain the questionId, questionName, videoUrl, score, and
 * answerId.
 * @param {string|undefined} userId - string|undefined
 * @param {string|undefined} interviewId - string|undefined
 * @returns An array of objects.
 */
export default function useGetInterviewQuestionsTableData(userId:string|undefined, interviewId: string|undefined) {
    return useQuery(["getQuestionsTable"], async () => {
        if(userId && interviewId){
            const questions = await InterviewQuestionService.getInterviewQuestions({userId, interviewId});
            const questionsData = questions.docs.map(async question => {
                const data = question.data();
                const answers = await AnswerService.getAnswers(question.ref);
                const submission = answers.docs.find(answer => answer.data().isSubmission);
                let videoDownloadUrl = undefined;
                if(submission?.data().videoUrl){
                    videoDownloadUrl = await StorageService.getDownloadUrlFromVideoUrlRef(submission.data().videoUrl);
                }
                return {
                    answerId: submission?.id,
                    questionId: question.id,
                    questionName: data.question,
                    videoUrl: videoDownloadUrl,
                    score: data.score,
                }
            });
            return Promise.all(questionsData);
        }
        return [];
    });
}