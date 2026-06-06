export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-warm-bg text-text-main">
      {children}
    </div>
  );
}
