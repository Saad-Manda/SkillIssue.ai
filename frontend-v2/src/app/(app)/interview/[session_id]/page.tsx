"use client";
import { useState, useEffect, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Send, FileText, BrainCircuit, Clock } from "lucide-react";
import { sessionApi } from "@/lib/api";
import { AppButton } from "@/components/primitives/AppButton";
import { ConfirmModal } from "@/components/primitives/ConfirmModal";
import { InterviewCompleteModal } from "@/components/primitives/InterviewCompleteModal";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";
import type { AnswerResponse } from "@/types/api";

// ── AI Thinking indicator ──────────────────────────────────────────
function AIThinking() {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 border border-brand-200 flex-shrink-0">
        <BrainCircuit size={14} className="text-brand-700" />
      </div>
      <div className="flex items-center gap-1.5 px-4 py-3 bg-white border border-warm-border rounded-2xl rounded-tl-sm shadow-warm-sm">
        <div className="flex gap-1 items-end h-4">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-brand-400"
              style={{ animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
            />
          ))}
        </div>
        <span className="text-sm text-text-muted ml-1">Thinking…</span>
      </div>
    </div>
  );
}

// ── Chat message ───────────────────────────────────────────────────
function ChatMessage({
  role,
  content,
  userInitials,
}: {
  role: "ai" | "user";
  content: string;
  userInitials: string;
}) {
  const isAI = role === "ai";

  return (
    <div className={cn("flex items-start gap-3", !isAI && "flex-row-reverse")}>
      {/* Avatar */}
      <div className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0",
        isAI ? "bg-brand-100 border border-brand-200" : "bg-stone-800"
      )}>
        {isAI
          ? <BrainCircuit size={14} className="text-brand-700" />
          : <span className="text-xs font-semibold text-white">{userInitials}</span>
        }
      </div>

      {/* Bubble */}
      <div className={cn(
        "max-w-[75%] px-4 py-3 text-sm leading-relaxed shadow-warm-sm",
        isAI
          ? "bg-white border border-warm-border rounded-2xl rounded-tl-sm text-text-main"
          : "bg-stone-900 rounded-2xl rounded-tr-sm text-white"
      )}>
        {content}
      </div>
    </div>
  );
}

// ── Elapsed timer ──────────────────────────────────────────────────
function ElapsedTimer({ startTime }: { startTime: Date }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime.getTime()) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [startTime]);

  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  return (
    <span className="font-mono text-xs text-text-muted tabular-nums">
      {mins.toString().padStart(2, "0")}:{secs.toString().padStart(2, "0")}
    </span>
  );
}

// ── Main Session Page ──────────────────────────────────────────────
export default function InterviewSessionPage() {
  const { session_id } = useParams<{ session_id: string }>();
  const router = useRouter();
  const { user } = useAuthStore();

  const [chat, setChat] = useState<{ role: "ai" | "user"; content: string }[]>([]);
  const [currentPhase, setCurrentPhase] = useState("Initializing…");
  const [currentTopic, setCurrentTopic] = useState("");
  const [turnCount, setTurnCount] = useState(0);
  const [inputMessage, setInputMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEndModal, setShowEndModal] = useState(false);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [startTime] = useState(new Date());

  const endRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load initial question from sessionStorage
  useEffect(() => {
    const stored = sessionStorage.getItem(`session_${session_id}`);
    if (stored) {
      const init = JSON.parse(stored) as {
        current_question: string;
        current_phase_name: string;
        current_topic_name?: string;
      };
      setChat([{ role: "ai", content: init.current_question }]);
      setCurrentPhase(init.current_phase_name ?? "Opening");
      setCurrentTopic(init.current_topic_name ?? "");
    } else {
      setChat([{ role: "ai", content: "Welcome! Press Enter to begin your interview." }]);
    }
  }, [session_id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, isProcessing]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isProcessing) return;

    const userMsg = inputMessage.trim();
    setChat((prev) => [...prev, { role: "user", content: userMsg }]);
    setInputMessage("");
    setIsProcessing(true);
    setError(null);

    try {
      const response = await sessionApi.submitAnswer(session_id, userMsg) as AnswerResponse;

      if (response.interview_complete) {
        // Store report inline if available (avoids extra fetch on report page)
        if (response.report) {
          sessionStorage.setItem(`report_${session_id}`, response.report);
        }
        setInterviewComplete(true);
      } else if (response.current_question) {
        setChat((prev) => [...prev, { role: "ai", content: response.current_question! }]);
        setCurrentPhase(response.current_phase_name ?? currentPhase);
        setCurrentTopic(response.current_topic_name ?? "");
        setTurnCount((c) => c + 1);
      }
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message ?? "Failed to submit answer. Please try again.");
      setChat((prev) => prev.slice(0, -1));
      setInputMessage(userMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const userInitials = (user?.username ?? user?.email ?? "U").slice(0, 2).toUpperCase();

  return (
    <>
      <div className="flex h-[calc(100vh-56px)]">
        {/* ── Sidebar ───────────────────────────────────────────────── */}
        <div className="w-72 flex-shrink-0 border-r border-warm-border bg-white flex flex-col">
          {/* Header */}
          <div className="px-5 py-4 border-b border-warm-border">
            <p className="text-xs font-semibold uppercase tracking-widest text-text-muted">
              Session Progress
            </p>
          </div>

          {/* Stats */}
          <div className="px-5 py-4 border-b border-warm-border grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-0.5">
              <p className="text-xs text-text-muted">Turn</p>
              <p className="text-2xl font-bold text-text-main tabular-nums">{turnCount}</p>
            </div>
            <div className="flex flex-col gap-0.5">
              <p className="text-xs text-text-muted">Elapsed</p>
              <div className="flex items-center gap-1 mt-0.5">
                <Clock size={12} className="text-text-muted" />
                <ElapsedTimer startTime={startTime} />
              </div>
            </div>
          </div>

          {/* Current Phase & Topic */}
          <div className="px-5 py-4 flex-1">
            <div className="mb-4">
              <p className="text-xs text-text-muted mb-1">Current Phase</p>
              <p className="text-sm font-semibold text-text-main">{currentPhase}</p>
            </div>
            {currentTopic && (
              <div>
                <p className="text-xs text-text-muted mb-1">Active Topic</p>
                <p className="text-sm text-text-secondary">{currentTopic}</p>
              </div>
            )}
          </div>

          {/* End interview */}
          <div className="px-5 py-4 border-t border-warm-border">
            <AppButton
              variant="outline"
              size="sm"
              fullWidth
              leftIcon={<FileText size={14} />}
              onClick={() => setShowEndModal(true)}
            >
              End & Get Report
            </AppButton>
          </div>
        </div>

        {/* ── Chat Canvas ──────────────────────────────────────────── */}
        <div className="flex-1 flex flex-col bg-warm-bg overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-8">
            <div className="max-w-2xl mx-auto space-y-5">
              {chat.map((msg, i) => (
                <ChatMessage
                  key={i}
                  role={msg.role}
                  content={msg.content}
                  userInitials={userInitials}
                />
              ))}

              {isProcessing && <AIThinking />}

              <div ref={endRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-warm-border bg-white px-6 py-4">
            <div className="max-w-2xl mx-auto">
              {error && (
                <div className="mb-3 text-xs text-error bg-error/8 border border-error/20 px-3 py-2 rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="flex gap-3 items-end">
                <div className="flex-1">
                  <textarea
                    ref={textareaRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    disabled={isProcessing || interviewComplete}
                    placeholder="Type your answer…"
                    rows={1}
                    className={cn(
                      "w-full resize-none rounded-xl border border-warm-border bg-warm-bg px-4 py-3",
                      "text-sm text-text-main placeholder:text-text-muted",
                      "focus:outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-600/20",
                      "disabled:opacity-50 transition-colors duration-150",
                      "max-h-48 overflow-y-auto"
                    )}
                    style={{ minHeight: "52px" }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e as unknown as React.FormEvent);
                      }
                    }}
                    aria-label="Your answer"
                  />
                  <p className="text-xs text-text-muted mt-1.5 pl-1">
                    Press <kbd className="px-1.5 py-0.5 bg-warm-muted rounded text-[10px] font-mono">Enter</kbd> to send
                    {" · "}
                    <kbd className="px-1.5 py-0.5 bg-warm-muted rounded text-[10px] font-mono">Shift + Enter</kbd> for new line
                  </p>
                </div>

                <AppButton
                  type="submit"
                  variant="brand"
                  size="md"
                  disabled={isProcessing || !inputMessage.trim() || interviewComplete}
                  isLoading={isProcessing}
                  className="mb-6"
                >
                  <Send size={16} />
                </AppButton>
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* CSS for AI thinking bounce animation */}
      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-8px); }
        }
      `}</style>

      {/* End interview confirmation */}
      <ConfirmModal
        open={showEndModal}
        onOpenChange={setShowEndModal}
        title="End interview?"
        description={`You've completed ${turnCount} turn${turnCount !== 1 ? "s" : ""}. Ending now will generate your readiness report.`}
        confirmLabel="End & Generate Report"
        cancelLabel="Continue Interview"
        variant="default"
        onConfirm={() => router.push(`/report/${session_id}`)}
      />

      {/* Auto-triggered when interview_complete is returned */}
      <InterviewCompleteModal
        open={interviewComplete}
        onNavigate={() => router.push(`/report/${session_id}`)}
      />
    </>
  );
}
