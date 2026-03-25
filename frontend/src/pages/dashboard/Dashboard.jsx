import { useEffect, useMemo, useState } from "react";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { useNavigate } from "react-router-dom";
import { Plus, History, Calendar, FileText } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { api } from "../../services/api";

export const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [interviews, setInterviews] = useState([]);
  const [isLoadingInterviews, setIsLoadingInterviews] = useState(true);
  const [historyError, setHistoryError] = useState(null);

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const allInterviews = await api.getAllInterviews();
        setInterviews(Array.isArray(allInterviews) ? allInterviews : []);
      } catch (err) {
        setHistoryError(err.message || "Failed to load interview history.");
      } finally {
        setIsLoadingInterviews(false);
      }
    };

    fetchInterviews();
  }, []);

  const userInterviews = useMemo(() => {
    const filtered = interviews.filter((interview) => {
      if (!user?.id) return true;
      return interview.user_id === user.id;
    });

    return filtered.sort((a, b) => {
      const aTime = a?.conducted_on ? new Date(a.conducted_on).getTime() : 0;
      const bTime = b?.conducted_on ? new Date(b.conducted_on).getTime() : 0;
      return bTime - aTime;
    });
  }, [interviews, user?.id]);

  return (
    <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "40px 20px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-end",
          marginBottom: "32px",
        }}
      >
        <div>
          <h1 style={{ fontSize: "32px", marginBottom: "8px" }}>Dashboard</h1>
          <p style={{ color: "var(--text-secondary)" }}>
            Welcome back! Ready for your next interview?
          </p>
        </div>
        <Button onClick={() => navigate("/interview/start")}>
          <Plus size={18} /> New Interview
        </Button>
      </div>

      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}
      >
        {/* Quick Stats / Profile Snapshot */}
        <Card title="Your Profile" style={{ margin: 0, height: "fit-content" }}>
          <div
            style={{ display: "flex", flexDirection: "column", gap: "16px" }}
          >
            <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
              Keep your profile comprehensive to get the best tailored
              interviews from the Planner agent.
            </p>
            <Button
              variant="secondary"
              onClick={() => navigate("/profile")}
              fullWidth
            >
              View Profile
            </Button>
          </div>
        </Card>

        {/* History */}
        <Card title="Recent Interviews" style={{ margin: 0, maxWidth: "none" }}>
          {isLoadingInterviews && (
            <p style={{ color: "var(--text-secondary)", padding: "8px 0" }}>
              Loading interview history...
            </p>
          )}

          {!isLoadingInterviews && historyError && (
            <div style={{ color: "#EF4444" }}>
              <p>{historyError}</p>
            </div>
          )}

          {!isLoadingInterviews &&
            !historyError &&
            userInterviews.length === 0 && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  padding: "40px 0",
                  color: "var(--text-secondary)",
                }}
              >
                <History
                  size={48}
                  style={{ opacity: 0.2, marginBottom: "16px" }}
                />
                <p>No interviews completed yet.</p>
                <p style={{ fontSize: "14px", marginTop: "8px" }}>
                  Start a new session to see your metrics and STAR analysis.
                </p>
              </div>
            )}

          {!isLoadingInterviews &&
            !historyError &&
            userInterviews.length > 0 && (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px",
                }}
              >
                {userInterviews.slice(0, 10).map((interview) => (
                  <div
                    key={interview._id}
                    style={{
                      border: "1px solid var(--border-color)",
                      borderRadius: "10px",
                      padding: "14px",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "12px",
                      backgroundColor: "var(--bg-secondary)",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        gap: "6px",
                      }}
                    >
                      <p
                        style={{
                          margin: 0,
                          fontWeight: 600,
                          color: "var(--text-primary)",
                        }}
                      >
                        Session: {interview.session_id || "N/A"}
                      </p>
                      <div
                        style={{
                          display: "flex",
                          gap: "14px",
                          color: "var(--text-secondary)",
                          fontSize: "14px",
                        }}
                      >
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                          }}
                        >
                          <Calendar size={14} />
                          {interview.conducted_on
                            ? new Date(interview.conducted_on).toLocaleString()
                            : "Unknown date"}
                        </span>
                        <span>JD: {interview.jd_id || "N/A"}</span>
                      </div>
                    </div>

                    <Button
                      variant="secondary"
                      onClick={() =>
                        navigate(`/interview/history/${interview._id}`)
                      }
                    >
                      <FileText size={16} /> Open
                    </Button>
                  </div>
                ))}
              </div>
            )}
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
