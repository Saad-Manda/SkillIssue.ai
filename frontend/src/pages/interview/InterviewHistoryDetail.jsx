import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { ArrowLeft, Briefcase, MessageSquare, FileText } from 'lucide-react';
import { api } from '../../services/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';

const formatMetricValue = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A';
  return value.toFixed(2);
};

export const InterviewHistoryDetail = () => {
  const { interview_id } = useParams();
  const navigate = useNavigate();

  const [interview, setInterview] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showJD, setShowJD] = useState(false);
  const [jdData, setJdData] = useState(null);
  const [jdLoading, setJdLoading] = useState(false);
  const [jdError, setJdError] = useState(null);

  useEffect(() => {
    const fetchInterview = async () => {
      try {
        const data = await api.getInterview(interview_id);
        setInterview(data);
      } catch (err) {
        setError(err.message || 'Failed to load interview.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchInterview();
  }, [interview_id]);

  const turns = useMemo(() => {
    if (!interview?.chat_history || !Array.isArray(interview.chat_history)) return [];
    return interview.chat_history;
  }, [interview]);

  const handleViewJD = async () => {
    if (!interview?.jd_id) {
      setJdError('No JD id found for this interview.');
      setShowJD(true);
      return;
    }

    setShowJD(true);
    setJdError(null);

    if (jdData?.id === interview.jd_id || jdData?.jd_id === interview.jd_id) return;

    setJdLoading(true);
    try {
      const data = await api.getJD(interview.jd_id);
      setJdData(data);
    } catch (err) {
      setJdError(err.message || 'Failed to load JD.');
    } finally {
      setJdLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '40px 20px' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading interview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '960px', margin: '0 auto', padding: '40px 20px' }}>
        <Card>
          <p style={{ color: '#EF4444', marginBottom: '16px' }}>{error}</p>
          <Button onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} /> Back to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '40px 20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <h1 style={{ fontSize: '32px', margin: 0 }}>Interview Details</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={16} /> Dashboard
          </Button>
          <Button onClick={handleViewJD}>
            <Briefcase size={16} /> View JD Used
          </Button>
        </div>
      </div>

      <Card style={{ maxWidth: '100%', margin: 0 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '12px', fontSize: '14px' }}>
          <p style={{ margin: 0 }}><strong>Interview ID:</strong> {interview?._id || 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>Session ID:</strong> {interview?.session_id || 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>User ID:</strong> {interview?.user_id || 'N/A'}</p>
          <p style={{ margin: 0 }}><strong>Conducted On:</strong> {interview?.conducted_on ? new Date(interview.conducted_on).toLocaleString() : 'N/A'}</p>
        </div>
      </Card>

      {showJD && (
        <Card title="Job Description Used" style={{ maxWidth: '100%', margin: 0 }}>
          {jdLoading && <p style={{ color: 'var(--text-secondary)' }}>Loading JD...</p>}
          {jdError && <p style={{ color: '#EF4444' }}>{jdError}</p>}
          {!jdLoading && !jdError && jdData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <p style={{ margin: 0 }}><strong>Job Title:</strong> {jdData.job_title || 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Job Type:</strong> {jdData.job_type || 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Min Experience:</strong> {jdData.min_experience ?? 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Required Qualification:</strong> {jdData.required_qualification || 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Description:</strong> {jdData.description || 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Required Skills:</strong> {Array.isArray(jdData.required_skills) ? jdData.required_skills.join(', ') : 'N/A'}</p>
              <p style={{ margin: 0 }}><strong>Responsibilities:</strong> {Array.isArray(jdData.responsibilities) ? jdData.responsibilities.join(' | ') : 'N/A'}</p>
            </div>
          )}
        </Card>
      )}

      <Card title="Final Report" style={{ maxWidth: '100%', margin: 0 }}>
        <div style={{ color: 'var(--text-primary)', lineHeight: '1.7' }}>
          <ReactMarkdown>{interview?.report || 'No report available.'}</ReactMarkdown>
        </div>
      </Card>

      <Card title="Chat History" style={{ maxWidth: '100%', margin: 0 }}>
        {turns.length === 0 && (
          <p style={{ color: 'var(--text-secondary)', margin: 0 }}>No chat history found for this interview.</p>
        )}

        {turns.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {turns.map((turn, index) => (
              <div key={turn.chat_id || `${index}`} style={{ border: '1px solid var(--border-color)', borderRadius: '10px', padding: '14px', backgroundColor: 'var(--bg-secondary)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px', color: 'var(--text-secondary)', fontSize: '14px' }}>
                  <MessageSquare size={14} />
                  <span>Turn {index + 1}</span>
                  <span>{turn.phase_name || 'Unknown phase'}</span>
                  <span>{turn.topic_id || 'Unknown topic'}</span>
                </div>
                <p style={{ margin: '0 0 8px 0' }}><strong>Question:</strong> {turn.question || 'N/A'}</p>
                <p style={{ margin: '0 0 10px 0' }}><strong>Response:</strong> {turn.response || 'N/A'}</p>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  <span>QAR: {formatMetricValue(turn?.metrics?.QAR)}</span>
                  <span>TDS: {formatMetricValue(turn?.metrics?.TDS)}</span>
                  <span>ACS: {formatMetricValue(turn?.metrics?.ACS)}</span>
                  <span>STAR: {formatMetricValue(turn?.metrics?.STAR_turn)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button onClick={() => window.print()}>
          <FileText size={16} /> Print
        </Button>
      </div>
    </div>
  );
};

export default InterviewHistoryDetail;
