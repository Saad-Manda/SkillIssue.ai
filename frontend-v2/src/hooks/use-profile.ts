import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import type { CreateProfilePayload } from "@/types/api";

export function useProfile() {
  const { user, token } = useAuthStore();
  return useQuery({
    queryKey: ["profile", user?.id],
    queryFn: () => usersApi.getProfile(user!.id, token!),
    enabled: !!user?.id && !!token,
    retry: false,  // Don't retry 404 (new user)
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { user, token } = useAuthStore();
  return useMutation({
    mutationFn: (data: Partial<CreateProfilePayload>) =>
      usersApi.updateProfile(user!.id, data, token!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile", user?.id] });
    },
  });
}

export function useCreateProfile() {
  const { signupToken, updateUser } = useAuthStore();
  return useMutation({
    mutationFn: (data: CreateProfilePayload) =>
      usersApi.createProfile(data, signupToken ?? ""),
    onSuccess: (result) => {
      updateUser({ id: result.user_id, email: result.email });
    },
  });
}
