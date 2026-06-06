"use client";
import { QueryClient, QueryClientProvider, QueryCache } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,     // 1 minute
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
        queryCache: new QueryCache({
          onError: (error: unknown) => {
            const err = error as { status?: number };
            if (err?.status === 401) {
              // Token expired — clear auth and redirect
              if (typeof window !== "undefined") {
                localStorage.removeItem("skillissue-auth");
                window.location.href = "/login";
              }
            }
          },
        }),
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
