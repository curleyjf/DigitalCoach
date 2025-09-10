import { useQuery } from "@tanstack/react-query";
import AnswerService from "./AnswerService";

export default function useGetAnswersByUserId(userId: string | undefined) {
  return useQuery({
    queryKey: ["getAnswersByUserId", userId], // Query key with userId to ensure it’s unique for each user
    queryFn: () => AnswerService.getAnswersByUserId(userId!), // Fetch function
    enabled: !!userId, // Only runs the query if userId is available
  });
}
