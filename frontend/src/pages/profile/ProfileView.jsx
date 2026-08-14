import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Loader2, Edit2, PlusCircle, Github, Linkedin, Briefcase, GraduationCap, Code, Trophy } from 'lucide-react';

export const ProfileView = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await api.getUserProfile(user.id, token);
        setProfile(data);
      } catch (err) {
        setError(err.message || 'Profile not found');
      } finally {
        setIsLoading(false);
      }
    };
    if (user?.id && token) {
      fetchProfile();
    } else {
      setIsLoading(false);
      setError("Not authenticated");
    }
  }, [user, token]);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Loader2 size={40} style={{ animation: 'spin 1.5s linear infinite', color: 'var(--accent-primary)' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '60px 20px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '24px', marginBottom: '16px' }}>No Profile Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>You haven't completed your comprehensive profile setup yet.</p>
        <Button onClick={() => navigate('/profile/new')}><PlusCircle size={16} /> Create Profile</Button>
      </div>
    );
  }

  const SectionTitle = ({ icon: Icon, title }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '24px', marginTop: '40px' }}>
      <Icon size={20} style={{ color: 'var(--accent-primary)' }} />
      <h2 style={{ fontSize: '20px', fontWeight: 600 }}>{title}</h2>
    </div>
  );

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px' }}>My Profile</h1>
        <Button onClick={() => navigate('/profile/update')}><Edit2 size={16} /> Edit Profile</Button>
      </div>

      <Card style={{ padding: '40px', marginBottom: '40px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '28px', fontWeight: 600 }}>{profile.name}</h2>
          <div style={{ display: 'flex', gap: '16px', color: 'var(--text-secondary)' }}>
            <span>{profile.email}</span>
            {profile.mobile && <span>• {profile.mobile}</span>}
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
            {profile.github_url && (
              <a href={`https://${profile.github_url.replace(/^https?:\/\//, '')}`} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-primary)', textDecoration: 'none' }}>
                <Github size={16} /> GitHub
              </a>
            )}
            {profile.linkedin_url && (
              <a href={`https://${profile.linkedin_url.replace(/^https?:\/\//, '')}`} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-primary)', textDecoration: 'none' }}>
                <Linkedin size={16} /> LinkedIn
              </a>
            )}
          </div>
        </div>

        {profile.skills?.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Top Skills</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {profile.skills.map((skill, i) => (
                <span key={i} style={{ padding: '4px 12px', backgroundColor: 'var(--bg-secondary)', borderRadius: '16px', fontSize: '14px' }}>{skill}</span>
              ))}
            </div>
          </div>
        )}

        {profile.experiences?.length > 0 && (
          <div>
            <SectionTitle icon={Briefcase} title="Experience" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {profile.experiences.map((exp, i) => (
                <div key={i} style={{ borderLeft: '2px solid var(--border-color)', paddingLeft: '16px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{exp.role} <span style={{ fontWeight: 400, color: 'var(--text-secondary)' }}>at {exp.company}</span></h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                    {exp.start_date} - {exp.end_date || 'Present'} • {exp.emp_type.replace('_', ' ')} • {exp.loc_type || 'Unknown'}
                  </p>
                  {exp.description && (
                    <p style={{ marginTop: '8px', fontSize: '15px', lineHeight: '1.6', marginBottom: '8px' }}>{exp.description}</p>
                  )}
                  {exp.skills_used?.length > 0 && (
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Skills: {exp.skills_used.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.educations?.length > 0 && (
          <div>
            <SectionTitle icon={GraduationCap} title="Education" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {profile.educations.map((edu, i) => (
                <div key={i} style={{ borderLeft: '2px solid var(--border-color)', paddingLeft: '16px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{edu.degree}</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                    {edu.institute_name} • Grade: {edu.grade} • {edu.start_date} - {edu.end_date || 'Present'}
                  </p>
                  {edu.courses?.length > 0 && (
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Courses: {edu.courses.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.projects?.length > 0 && (
          <div>
            <SectionTitle icon={Code} title="Projects" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {profile.projects.map((proj, i) => (
                <div key={i} style={{ borderLeft: '2px solid var(--border-color)', paddingLeft: '16px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600, display: 'flex', gap: '12px', alignItems: 'center' }}>
                    {proj.title}
                    {proj.github_url && <a href={`https://${proj.github_url.replace(/^https?:\/\//, '')}`} target="_blank" rel="noreferrer" style={{ color: 'var(--text-secondary)' }}><Github size={16}/></a>}
                  </h3>
                  <p style={{ marginTop: '8px', fontSize: '15px', lineHeight: '1.6' }}>{proj.description}</p>
                  {proj.skills_used?.length > 0 && (
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '8px' }}>Built with: {proj.skills_used.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {profile.leaderships?.length > 0 && (
          <div>
            <SectionTitle icon={Trophy} title="Leadership" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {profile.leaderships.map((ld, i) => (
                <div key={i} style={{ borderLeft: '2px solid var(--border-color)', paddingLeft: '16px' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: 600 }}>{ld.position} <span style={{ fontWeight: 400, color: 'var(--text-secondary)' }}>at {ld.committee_name}</span></h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                    {ld.start_date} - {ld.end_date || 'Present'}
                  </p>
                  {ld.description && (
                    <p style={{ marginTop: '8px', fontSize: '15px', lineHeight: '1.6', marginBottom: '8px' }}>{ld.description}</p>
                  )}
                  {ld.skills_used?.length > 0 && (
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Skills: {ld.skills_used.join(', ')}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      </Card>
    </div>
  );
};

export default ProfileView;
