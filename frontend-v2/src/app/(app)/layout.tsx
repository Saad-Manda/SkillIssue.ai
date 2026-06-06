export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-warm-bg text-text-main">
      <main>{children}</main>
    </div>
  );
}
