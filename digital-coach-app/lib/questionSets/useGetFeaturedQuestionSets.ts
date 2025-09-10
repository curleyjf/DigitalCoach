import { useQuery } from "@tanstack/react-query";
import QuestionSetsService from "./QuestionSetsService";

export default function useGetFeaturedQuestionSets() {
  return useQuery({
    queryKey: ["featuredQuestionSets"], // Query key
    queryFn: () => QuestionSetsService.getFeaturedQuestionSets(), // Fetch function
  });
}
