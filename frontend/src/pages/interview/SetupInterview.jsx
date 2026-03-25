import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';

export const SetupInterview = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    job_title: '',
    min_experience: '',
    required_skills: '',
    job_type: 'full_time', // Complies with Emp_Type enum
    required_qualification: 'Bachelors',
    responsibilities: '',
    description: ''
  });

  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // 1. Create JD
      const skillsArray = formData.required_skills.split(',').map(s => s.trim()).filter(s => s);
      const respsArray = formData.responsibilities.split('\n').filter(s => s);
      
      const payload = {
        job_title: formData.job_title,
        job_type: formData.job_type,
        min_experience: parseFloat(formData.min_experience) || 0,
        required_skills: skillsArray,
        responsibilities: respsArray.length ? respsArray : ["General responsibilities"],
        required_qualification: formData.required_qualification,
        description: formData.description
      };

      // Assuming the backend has been updated to remove enum strictness or accepts string equivalents
      // For MVP, we pass the basic object.
      const jdData = await api.createJD(payload);
      
      // The backend model might use an id field like 'jd_id' or 'id'
      const jdId = jdData.jd_id || jdData.id;

      if (!jdId) {
         throw new Error("Failed to retrieve ID for the created Job Description");
      }

      // 2. Start Session
      // Passing 'short' as interview length for testing
      const sessionInit = await api.startInterview(user.id, jdId, 'short');
      
      // Store initial state locally to pass to the session page
      navigate(`/interview/${sessionInit.session_id}`, { state: { initialSession: sessionInit } });

    } catch (err) {
      setError(err.message || 'Failed to start interview');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Setup New Interview</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
        Provide the target Job Description to contextualize the AI.
      </p>

      <Card style={{ maxWidth: '100%' }}>
        {error && (
          <div style={{ padding: '12px', backgroundColor: '#FEF2F2', color: '#EF4444', borderRadius: '6px', marginBottom: '16px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '16px' }}>
          
          <Input label="Job Title" name="job_title" value={formData.job_title} onChange={handleChange} required placeholder="e.g. Senior Frontend Engineer" />
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Input label="Min Experience (years)" name="min_experience" type="number" min="0" step="0.5" value={formData.min_experience} onChange={handleChange} required placeholder="3" />
            <Input label="Required Qualification" name="required_qualification" value={formData.required_qualification} onChange={handleChange} required placeholder="Bachelors in CS" />
          </div>

          <Input label="Required Skills (comma separated)" name="required_skills" value={formData.required_skills} onChange={handleChange} required placeholder="React, TypeScript, GraphQL" />
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px' }}>
            <label style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Responsibilities (One per line)</label>
            <textarea 
              name="responsibilities"
              value={formData.responsibilities}
              onChange={handleChange}
              style={{
                width: '100%', padding: '10px 14px', border: '1px solid var(--border-color)', borderRadius: '6px',
                minHeight: '80px', fontFamily: 'inherit', fontSize: '15px'
              }}
              placeholder="Develop scalable UIs..."
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px' }}>
            <label style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>Full Job Description</label>
            <textarea 
              name="description"
              value={formData.description}
              onChange={handleChange}
              style={{
                width: '100%', padding: '10px 14px', border: '1px solid var(--border-color)', borderRadius: '6px',
                minHeight: '120px', fontFamily: 'inherit', fontSize: '15px'
              }}
              placeholder="Paste full JD here for better context..."
            />
          </div>

          <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <Button type="button" onClick={() => navigate('/dashboard')}>Cancel</Button>
            <Button type="submit" isLoading={isLoading}>Start Interview</Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default SetupInterview;
