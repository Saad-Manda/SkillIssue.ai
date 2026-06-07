import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  username: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  signupToken: string | null;   // Temporary token used in createUserProfile
  isAuthenticated: boolean;

  setAuth: (token: string, user: User) => void;
  setSignupToken: (token: string) => void;
  clearAuth: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      signupToken: null,
      isAuthenticated: false,

      setAuth: (token, user) => set({ token, user, isAuthenticated: true }),
      setSignupToken: (signupToken) => set({ signupToken }),
      clearAuth: () => set({ token: null, user: null, isAuthenticated: false }),
      updateUser: (partialUser) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partialUser } : null,
        })),
    }),
    {
      name: "skillissue-auth",  // localStorage key
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        signupToken: state.signupToken,
      }),
    }
  )
);
