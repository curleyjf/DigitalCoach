import { useQuery } from "@tanstack/react-query";
import InterviewQuestionService from "./InterviewQuestionService";

export default function useGetUserAverageScore(userId: string | undefined) {
  return useQuery({
    queryKey: ["getUserScores", userId], // Add userId to the query key to track changes
    queryFn: () => {
      if (userId) {
        return InterviewQuestionService.getUserAverageScore(userId);
      }
      return 0; // Return 0 if no userId
    },
    enabled: !!userId, // Only run the query if userId is available
  });
}
