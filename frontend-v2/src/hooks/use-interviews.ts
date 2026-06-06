import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { interviewApi, jdApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

export function useInterviews() {
  const { user } = useAuthStore();
  return useQuery({
    queryKey: ["interviews", user?.id],
    queryFn: () => interviewApi.getAll(user!.id),
    enabled: !!user?.id,
  });
}

export function useInterviewDetail(interviewId: string) {
  const { user } = useAuthStore();
  return useQuery({
    queryKey: ["interview", interviewId],
    queryFn: async () => {
      const interview = await interviewApi.getDetails(user!.id, interviewId);
      let jd = null;
      if (interview.jd_id) {
        jd = await jdApi.get(interview.jd_id).catch(() => null);
      }
      return { interview, jd };
    },
    enabled: !!user?.id && !!interviewId,
  });
}

export function useDeleteInterview() {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  return useMutation({
    mutationFn: (interviewId: string) => interviewApi.delete(interviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", user?.id] });
    },
  });
}
