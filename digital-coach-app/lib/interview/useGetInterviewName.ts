import { useQuery } from "@tanstack/react-query";
import InterviewService from "./InterviewService";

/**
 * It returns the title of an interview, given the userId and interviewId.
 * @param {string | undefined | null} userId - string | undefined | null
 * @param {string | undefined | null} interviewId - string | undefined | null
 * @returns The title of the interview.
 */
export default function useGetInterviewName(userId: string | undefined | null, interviewId: string | undefined | null) {
    return useQuery(["getInterviewName"], async () => {
        if(userId && interviewId) {
            const interview = await InterviewService.fetchInterview({userId, interviewId});
            return interview?.data()?.title;
        }
        else return null;
    })
}

