import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths without auth check
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Check for auth token in localStorage via a cookie mirror
  // NOTE: We can't read localStorage in middleware (server-side).
  // Strategy: On login, we ALSO set a lightweight cookie "skillissue-authed=1"
  // (non-HttpOnly, no sensitive data) just to signal auth state in middleware.
  const isAuthed = request.cookies.get("skillissue-authed")?.value === "1";

  if (!isAuthed && !pathname.startsWith("/_next")) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Skip _next internals, api routes, and any path that looks like a static file (has an extension)
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)",
  ],
};
