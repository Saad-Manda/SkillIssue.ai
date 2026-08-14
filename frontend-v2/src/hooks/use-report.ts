import { useQuery } from "@tanstack/react-query";
import { sessionApi } from "@/lib/api";

export function useReport(sessionId: string) {
  return useQuery({
    queryKey: ["report", sessionId],
    queryFn: () => sessionApi.getReport(sessionId),
    enabled: !!sessionId,
    // Poll every 3s until report arrives (handles async generation)
    refetchInterval: (query) => (query.state.data?.report ? false : 3000),
    refetchIntervalInBackground: false,
    retry: 3,
  });
}
