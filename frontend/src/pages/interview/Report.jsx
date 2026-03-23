import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { api } from '../../services/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Loader2, ArrowLeft, Download } from 'lucide-react';

export const Report = () => {
  const { session_id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await api.getReport(session_id);
        setReport(data.report || "No report generated.");
      } catch (err) {
        setError(err.message || "Failed to load report.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, [session_id]);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 'calc(100vh - 100px)' }}>
        <Loader2 size={40} style={{ animation: 'spin 1.5s linear infinite', color: 'var(--accent-primary)', marginBottom: '16px' }} />
        <h2 style={{ fontSize: '20px', color: 'var(--text-primary)' }}>Generating Readiness Report...</h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>The Report Generator Agent is analyzing your performance.</p>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
        <Card>
          <div style={{ color: '#EF4444', marginBottom: '16px' }}>Error: {error}</div>
          <Button onClick={() => navigate('/dashboard')}>Return to Dashboard</Button>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px' }}>Interview Readiness Report</h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Button variant="secondary" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} /> Dashboard
          </Button>
          <Button onClick={() => window.print()}>
            <Download size={16} /> Export PDF
          </Button>
        </div>
      </div>

      <Card style={{ maxWidth: '100%', padding: '40px' }}>
        <div className="markdown-body" style={{ color: 'var(--text-primary)', lineHeight: '1.7', fontSize: '16px' }}>
          {/* Use Jost font for general styling, but let react-markdown handle the headers/boldings natively */}
          <ReactMarkdown
            components={{
              h1: ({node, ...props}) => <h1 style={{ fontSize: '28px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '24px', marginTop: '32px' }} {...props} />,
              h2: ({node, ...props}) => <h2 style={{ fontSize: '22px', marginBottom: '16px', marginTop: '24px' }} {...props} />,
              h3: ({node, ...props}) => <h3 style={{ fontSize: '18px', marginBottom: '12px', marginTop: '20px' }} {...props} />,
              p: ({node, ...props}) => <p style={{ marginBottom: '16px' }} {...props} />,
              ul: ({node, ...props}) => <ul style={{ marginBottom: '16px', paddingLeft: '24px' }} {...props} />,
              li: ({node, ...props}) => <li style={{ marginBottom: '8px' }} {...props} />,
              strong: ({node, ...props}) => <strong style={{ fontWeight: 600, color: 'var(--accent-primary)' }} {...props} />
            }}
          >
            {report}
          </ReactMarkdown>
        </div>
      </Card>
      
      {/* Hide printable artifacts when printing */}
      <style>{`
        @media print {
          nav, button { display: none !important; }
          .markdown-body { color: #000 !important; }
        }
      `}</style>
    </div>
  );
};

export default Report;
