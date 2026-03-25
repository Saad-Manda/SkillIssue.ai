import { useState, useEffect } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { Plus, History, Trash2, Calendar, FileText } from 'lucide-react';
import { api } from '../../services/api';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const data = await api.getAllInterviews();
        setInterviews(data);
      } catch (error) {
        console.error('Failed to fetch interviews:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchInterviews();
  }, []);

  const handleDelete = async (e, interviewId) => {
    e.stopPropagation(); // prevent navigating to details
    if (!window.confirm("Are you sure you want to delete this interview?")) return;
    try {
      await api.deleteInterview(interviewId);
      setInterviews((prev) => prev.filter((inv) => inv._id !== interviewId));
    } catch (error) {
      console.error('Failed to delete interview:', error);
      alert("Failed to delete interview.");
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Welcome back! Ready for your next interview?</p>
        </div>
        <Button onClick={() => navigate('/interview/start')}>
          <Plus size={18} /> New Interview
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        {/* Quick Stats / Profile Snapshot */}
        <Card title="Your Profile" style={{ margin: 0, height: 'fit-content' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Keep your profile comprehensive to get the best tailored interviews from the Planner agent.</p>
            <Button variant="secondary" onClick={() => navigate('/profile')} fullWidth>
              View Profile
            </Button>
          </div>
        </Card>

        {/* History */}
        <Card title="Recent Interviews" style={{ margin: 0, maxWidth: 'none' }}>
          {loading ? (
            <p style={{ textAlign: 'center', padding: '40px 0' }}>Loading interviews...</p>
          ) : interviews.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 0', color: 'var(--text-secondary)' }}>
              <History size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
              <p>No interviews completed yet.</p>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>Start a new session to see your metrics and STAR analysis.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {interviews.map((inv) => (
                <div 
                  key={inv._id}
                  onClick={() => navigate(`/interview/details/${inv._id}`)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '16px',
                    borderRadius: '8px',
                    backgroundColor: 'var(--bg-tertiary)',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                    border: '1px solid var(--border-color)'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)'}
                >
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <Calendar size={16} />
                      <span style={{ fontWeight: '500' }}>{new Date(inv.conducted_on).toLocaleString()}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '14px' }}>
                      <FileText size={14} />
                      <span>JD ID: {inv.jd_id.substring(0, 8)}...</span>
                      <span>Session: {inv.session_id.substring(0, 8)}...</span>
                    </div>
                  </div>
                  <button 
                    onClick={(e) => handleDelete(e, inv._id)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--error-color, #ef4444)',
                      cursor: 'pointer',
                      padding: '8px'
                    }}
                    title="Delete Interview"
                  >
                    <Trash2 size={20} />
                  </button>
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
