import { useQuery } from "@tanstack/react-query";
import InterviewService from "./InterviewService";

/**
 * It returns the result of a query that fetches the user's interviews from the database.
 * @param {string | undefined} userId - string | undefined
 * @returns An array of interviews
 */
export default function useFetchUserInterviews(userId: string | undefined) {
    return useQuery(["fetchUserInterviews"], () => {
        if(userId) return InterviewService.fetchUserInterviews(userId);
        else return null;
    })
} //wrote this by accident but we'll prob need it later
