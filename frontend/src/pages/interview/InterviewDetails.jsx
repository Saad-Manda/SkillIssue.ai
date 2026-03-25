import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../../services/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ArrowLeft, Briefcase, FileText, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const InterviewDetails = () => {
  const { interview_id } = useParams();
  const navigate = useNavigate();

  const [interview, setInterview] = useState(null);
  const [jd, setJd] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showJd, setShowJd] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const interviewData = await api.getInterviewDetails(interview_id);
        setInterview(interviewData);

        if (interviewData && interviewData.jd_id) {
          try {
            const jdData = await api.getJDDetails(interviewData.jd_id);
            setJd(jdData);
          } catch (jdError) {
            console.error('Failed to fetch JD:', jdError);
            // Non-critical, just keep jd as null
          }
        }
      } catch (err) {
        console.error('Failed to fetch interview details:', err);
        setError('Failed to load interview details.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [interview_id]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '100px 20px' }}>Loading interview details...</div>;
  }

  if (error || !interview) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 20px', color: 'var(--error-color, #ef4444)' }}>
        <h2>{error || 'Interview not found'}</h2>
        <Button onClick={() => navigate('/dashboard')} style={{ marginTop: '20px' }}>Back to Dashboard</Button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px 20px' }}>
      <Button variant="secondary" onClick={() => navigate('/dashboard')} style={{ marginBottom: '24px' }}>
        <ArrowLeft size={16} /> Back to Dashboard
      </Button>

      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Interview Report</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Session ID: {interview.session_id} | Conducted on: {new Date(interview.conducted_on).toLocaleString()}
        </p>
      </div>

      {jd && (
        <Card style={{ marginBottom: '24px' }}>
          <div 
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
            onClick={() => setShowJd(!showJd)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500' }}>
              <Briefcase size={20} />
              <span>Job Description Used: {jd.job_title} at {jd.company_name}</span>
            </div>
            {showJd ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>
          
          {showJd && (
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
              <p><strong>Required Experience:</strong> {jd.required_experience} years</p>
              <div style={{ marginTop: '12px' }}>
                <strong>Description:</strong>
                <p style={{ whiteSpace: 'pre-line', color: 'var(--text-secondary)', marginTop: '8px' }}>{jd.job_description}</p>
              </div>
            </div>
          )}
        </Card>
      )}

      {interview.report && (
        <Card title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} />
            <span>AI Report</span>
          </div>
        } style={{ marginBottom: '24px' }}>
          <div style={{ lineHeight: '1.6', color: 'var(--text-primary)' }}>
            <ReactMarkdown>{interview.report}</ReactMarkdown>
          </div>
        </Card>
      )}

      <Card title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={20} />
          <span>Chat History</span>
        </div>
      }>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {interview.chat_history && interview.chat_history.length > 0 ? (
            interview.chat_history.map((turn, index) => (
              <div key={turn.chat_id || index} style={{ 
                padding: '16px', 
                backgroundColor: 'var(--bg-tertiary)', 
                borderRadius: '8px',
                border: '1px solid var(--border-color)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                  <span>Phase: {turn.phase_name}</span>
                  <span>Topic ID: {turn.topic_id}</span>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  <p style={{ fontWeight: '500', marginBottom: '8px', color: 'var(--primary-color)' }}>
                    <strong>Interviewer:</strong> {turn.question}
                  </p>
                  <p style={{ paddingLeft: '16px', borderLeft: '3px solid var(--border-color)' }}>
                    <strong>You:</strong> {turn.response}
                  </p>
                </div>

                {turn.metrics && (
                  <div style={{ 
                    marginTop: '16px', 
                    paddingTop: '16px', 
                    borderTop: '1px dotted var(--border-color)',
                    fontSize: '14px'
                  }}>
                    <strong style={{ display: 'block', marginBottom: '8px' }}>Metrics & Feedback:</strong>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', color: 'var(--text-secondary)' }}>
                      <span>Relevance: {turn.metrics.relevance_score || 'N/A'}</span>
                      <span>Clarity: {turn.metrics.clarity_score || 'N/A'}</span>
                      <span>Completeness: {turn.metrics.completeness_score || 'N/A'}</span>
                    </div>
                    {turn.metrics.feedback && (
                      <p style={{ marginTop: '8px', fontStyle: 'italic' }}>
                        &quot;{turn.metrics.feedback}&quot;
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--text-secondary)' }}>No chat history available for this session.</p>
          )}
        </div>
      </Card>
    </div>
  );
};

export default InterviewDetails;
