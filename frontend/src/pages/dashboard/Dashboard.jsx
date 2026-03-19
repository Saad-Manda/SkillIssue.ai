import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { Plus, History } from 'lucide-react';

export const Dashboard = () => {
  const navigate = useNavigate();

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
              Update Profile
            </Button>
          </div>
        </Card>

        {/* History */}
        <Card title="Recent Interviews" style={{ margin: 0, maxWidth: 'none' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 0', color: 'var(--text-secondary)' }}>
            <History size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
            <p>No interviews completed yet.</p>
            <p style={{ fontSize: '14px', marginTop: '8px' }}>Start a new session to see your metrics and STAR analysis.</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
