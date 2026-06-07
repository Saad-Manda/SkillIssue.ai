"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BrainCircuit, LayoutDashboard, User, Plus, LogOut, Settings } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { InitialsAvatar } from "@/components/primitives/InitialsAvatar";
import { AppButton } from "@/components/primitives/AppButton";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/profile",   label: "Profile",   icon: User           },
];

export function Navbar() {
  const pathname  = usePathname();
  const router    = useRouter();
  const { user, token, clearAuth } = useAuthStore();

  const handleLogout = async () => {
    try {
      if (token) await authApi.logout(token);
    } catch {
      // Ignore logout API errors — clear client state regardless
    }
    // Remove auth middleware cookie
    document.cookie = "skillissue-authed=; path=/; max-age=0";
    clearAuth();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-warm-border bg-white/80 backdrop-blur-sm">
      <nav
        className="flex h-14 items-center justify-between px-4 md:px-8 max-w-screen-xl mx-auto"
        aria-label="Main navigation"
      >
        {/* Left — Logo + Nav links */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand-600">
              <BrainCircuit size={16} className="text-white" />
            </div>
            <span className="font-semibold text-text-main text-sm tracking-tight hidden sm:block">
              SkillIssue.ai
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ href, label, icon: Icon }) => {
              const isActive = pathname === href || pathname.startsWith(`${href}/`);
              return (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium",
                    "transition-colors duration-150",
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-text-secondary hover:text-text-main hover:bg-warm-muted"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon size={16} />
                  {label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Right — New Interview shortcut + User menu */}
        <div className="flex items-center gap-3">
          <AppButton
            variant="brand"
            size="sm"
            leftIcon={<Plus size={14} />}
            onClick={() => router.push("/interview/setup")}
            className="hidden sm:inline-flex"
          >
            New Interview
          </AppButton>

          {/* User Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-600 rounded-full"
                aria-label="Open user menu"
              >
                <InitialsAvatar name={user?.username ?? user?.email} size="sm" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52 bg-white border-warm-border shadow-warm-lg">
              {/* User info */}
              <div className="px-3 py-2 border-b border-warm-border">
                <p className="text-sm font-medium text-text-main truncate">
                  {user?.username ?? "User"}
                </p>
                <p className="text-xs text-text-muted truncate">{user?.email}</p>
              </div>

              <DropdownMenuItem asChild>
                <Link href="/profile" className="flex items-center gap-2 cursor-pointer">
                  <User size={14} /> My Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="#" className="flex items-center gap-2 cursor-pointer text-text-muted">
                  <Settings size={14} /> Settings
                </Link>
              </DropdownMenuItem>

              <DropdownMenuSeparator />

              <DropdownMenuItem
                onClick={handleLogout}
                className="flex items-center gap-2 text-error focus:text-error focus:bg-error/8 cursor-pointer"
              >
                <LogOut size={14} /> Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </header>
  );
}
