import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { Plus, Trash2 } from 'lucide-react';

// Reusable Section Component
const FormSection = ({ title, children }) => (
  <div style={{ marginBottom: '40px', paddingBottom: '32px', borderBottom: '1px solid var(--border-color)' }}>
    <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '24px' }}>{title}</h2>
    {children}
  </div>
);

// Dynamic Array Item Wrapper
const ArrayItem = ({ index, onRemove, children }) => (
  <div style={{ 
    padding: '24px', backgroundColor: '#F9FAFB', border: '1px solid var(--border-color)', 
    borderRadius: '12px', marginBottom: '16px', position: 'relative' 
  }}>
    <button 
      type="button" onClick={() => onRemove(index)}
      style={{
        position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', 
        color: '#EF4444', cursor: 'pointer', padding: '4px'
      }}
    >
      <Trash2 size={18} />
    </button>
    {children}
  </div>
);

export const Profile = () => {
  const { user, token, setUser } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [hasExistingProfile, setHasExistingProfile] = useState(false);
  const toDateInput = (value) => (typeof value === 'string' ? value.split('T')[0] : (value || ''));

  // 1. Basic Info
  const [basics, setBasics] = useState({ name: '', mobile: '', github_url: '', linkedin_url: '', skills: '' });
  const handleBasics = (e) => setBasics({ ...basics, [e.target.name]: e.target.value });

  // Prefetch profile data
  useEffect(() => {
    if (user && user.id && token) {
      const fetchProfile = async () => {
        try {
          const data = await api.getUserProfile(user.id, token);
          if (data) {
            setHasExistingProfile(true);
            setBasics({
              name: data.name || '', mobile: data.mobile || '',
              github_url: data.github_url || '', linkedin_url: data.linkedin_url || '',
              skills: Array.isArray(data.skills) ? data.skills.join(', ') : ''
            });
            if (data.experiences) {
              setExperiences(data.experiences.map(ex => ({
                ...ex,
                start_date: toDateInput(ex.start_date),
                end_date: toDateInput(ex.end_date),
                skills_used: Array.isArray(ex.skills_used) ? ex.skills_used.join(', ') : ''
              })));
            }
            if (data.educations) {
              setEducations(data.educations.map(ed => ({
                ...ed,
                start_date: toDateInput(ed.start_date),
                end_date: toDateInput(ed.end_date),
                courses: Array.isArray(ed.courses) ? ed.courses.join(', ') : ''
              })));
            }
            if (data.projects) {
              setProjects(data.projects.map(pr => ({ ...pr, skills_used: Array.isArray(pr.skills_used) ? pr.skills_used.join(', ') : '' })));
            }
            if (data.leaderships) {
              setLeaderships(data.leaderships.map(ld => ({
                ...ld,
                start_date: toDateInput(ld.start_date),
                end_date: toDateInput(ld.end_date),
                skills_used: Array.isArray(ld.skills_used) ? ld.skills_used.join(', ') : ''
              })));
            }
          }
        } catch (err) {
          setHasExistingProfile(false);
          console.log("Profile not found or could not be loaded entirely yet.", err);
        }
      };
      // Skip if explicitly on /profile/new to avoid overriding blank slate, 
      // although even on /new pre-filling isn't inherently bad if they already have one.
      fetchProfile();
    }
  }, [user, token]);

  // 2. Experiences
  const [experiences, setExperiences] = useState([]);
  const addExperience = () => setExperiences([...experiences, { 
    role: '', company: '', emp_type: 'full_time', start_date: '', end_date: '', 
    loc_type: 'onsite', location: '', description: '', skills_used: '' 
  }]);
  const updateExperience = (i, e) => {
    const newArr = [...experiences];
    newArr[i][e.target.name] = e.target.value;
    setExperiences(newArr);
  };
  const removeExperience = (i) => setExperiences(experiences.filter((_, idx) => idx !== i));

  // 3. Educations
  const [educations, setEducations] = useState([]);
  const addEducation = () => setEducations([...educations, { 
    institute_name: '', degree: '', grade: '', courses: '', start_date: '', end_date: '' 
  }]);
  const updateEducation = (i, e) => {
    const newArr = [...educations];
    newArr[i][e.target.name] = e.target.value;
    setEducations(newArr);
  };
  const removeEducation = (i) => setEducations(educations.filter((_, idx) => idx !== i));

  // 4. Projects
  const [projects, setProjects] = useState([]);
  const addProject = () => setProjects([...projects, { 
    title: '', description: '', skills_used: '', github_url: '', deployed_url: '' 
  }]);
  const updateProject = (i, e) => {
    const newArr = [...projects];
    newArr[i][e.target.name] = e.target.value;
    setProjects(newArr);
  };
  const removeProject = (i) => setProjects(projects.filter((_, idx) => idx !== i));

  // 5. Leaderships
  const [leaderships, setLeaderships] = useState([]);
  const addLeadership = () => setLeaderships([...leaderships, { 
    committee_name: '', position: '', skills_used: '', description: '', start_date: '', end_date: '' 
  }]);
  const updateLeadership = (i, e) => {
    const newArr = [...leaderships];
    newArr[i][e.target.name] = e.target.value;
    setLeaderships(newArr);
  };
  const removeLeadership = (i) => setLeaderships(leaderships.filter((_, idx) => idx !== i));


  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true); setError(null); setSuccess(false);

    try {
      // Clean and format arrays
      const splitStr = (str) => str ? str.split(',').map(s => s.trim()).filter(Boolean) : [];

      const payload = {
        name: basics.name, mobile: basics.mobile, github_url: basics.github_url, linkedin_url: basics.linkedin_url,
        skills: splitStr(basics.skills),
        experiences: experiences.map(ex => ({
          ...ex, skills_used: splitStr(ex.skills_used), 
          start_date: ex.start_date || new Date().toISOString().split('T')[0], 
          end_date: ex.end_date || new Date().toISOString().split('T')[0]
        })),
        educations: educations.map(ed => ({
          ...ed, courses: splitStr(ed.courses), grade: parseFloat(ed.grade) || 0.0,
          start_date: ed.start_date || new Date().toISOString().split('T')[0], 
          end_date: ed.end_date || new Date().toISOString().split('T')[0]
        })),
        projects: projects.map(pr => ({ ...pr, skills_used: splitStr(pr.skills_used) })),
        leaderships: leaderships.map(ld => ({
          ...ld, skills_used: splitStr(ld.skills_used),
          start_date: ld.start_date || new Date().toISOString().split('T')[0], 
          end_date: ld.end_date || new Date().toISOString().split('T')[0]
        }))
      };

      if (hasExistingProfile && user?.id) {
        await api.updateUserProfile(user.id, payload, token);
      } else {
        const signupToken = localStorage.getItem('signup_token');
        const createPayload = {
          user_id: user?.id || '',
          email: user?.email || 'user@example.com',
          username: user?.username || 'user',
          hashed_password: 'placeholder',
          is_active: true,
          ...payload
        };
        const createdUser = await api.createUserProfile(createPayload, signupToken || '');
        setUser({ id: createdUser.user_id, email: createdUser.email, username: createdUser.username });
      }
      
      setSuccess(true);
      setTimeout(() => navigate('/dashboard'), 1500);
      
    } catch (err) {
      setError(err.message || 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Comprehensive Profile</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
        Provide your full background to let the AI Interviewer contextualize its questions perfectly.
      </p>

      <Card style={{ maxWidth: '100%', padding: '40px' }}>
        {error && <div style={{ padding: '12px', backgroundColor: '#FEF2F2', color: '#EF4444', borderRadius: '6px', marginBottom: '24px' }}>{error}</div>}
        {success && <div style={{ padding: '12px', backgroundColor: '#F0FDF4', color: '#16A34A', borderRadius: '6px', marginBottom: '24px' }}>Profile saved successfully! Redirecting...</div>}

        <form onSubmit={handleSubmit}>
          
          {/* Basics */}
          <FormSection title="Basic Information">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <Input label="Full Name" name="name" value={basics.name} onChange={handleBasics} required placeholder="John Doe" />
              <Input label="Mobile" name="mobile" value={basics.mobile} onChange={handleBasics} placeholder="+1 ..." />
              <Input label="GitHub URL" name="github_url" value={basics.github_url} onChange={handleBasics} placeholder="github.com/..." />
              <Input label="LinkedIn URL" name="linkedin_url" value={basics.linkedin_url} onChange={handleBasics} placeholder="linkedin.com/in/..." />
            </div>
            <div style={{ marginTop: '16px' }}>
              <Input label="Top Skills (comma separated)" name="skills" value={basics.skills} onChange={handleBasics} required placeholder="Python, React, System Design" />
            </div>
          </FormSection>

          {/* Experiences */}
          <FormSection title="Experience">
            {experiences.map((exp, i) => (
              <ArrayItem key={exp.experience_id || i} index={i} onRemove={removeExperience}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <Input label="Role" name="role" value={exp.role} onChange={(e) => updateExperience(i, e)} required />
                  <Input label="Company" name="company" value={exp.company} onChange={(e) => updateExperience(i, e)} required />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <label style={{ fontSize: '14px', fontWeight: 500 }}>Type</label>
                    <select name="emp_type" value={exp.emp_type} onChange={(e) => updateExperience(i, e)} style={{ padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                      <option value="full_time">Full Time</option>
                      <option value="part_time">Part Time</option>
                    </select>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <label style={{ fontSize: '14px', fontWeight: 500 }}>Location Type</label>
                    <select name="loc_type" value={exp.loc_type} onChange={(e) => updateExperience(i, e)} style={{ padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                      <option value="onsite">On-site</option>
                      <option value="remote">Remote</option>
                    </select>
                  </div>
                  <Input label="Start Date" type="date" name="start_date" value={exp.start_date} onChange={(e) => updateExperience(i, e)} required />
                  <Input label="End Date" type="date" name="end_date" value={exp.end_date} onChange={(e) => updateExperience(i, e)} />
                </div>
                <div style={{ marginTop: '16px' }}>
                  <Input label="Skills Used (comma separated)" name="skills_used" value={exp.skills_used} onChange={(e) => updateExperience(i, e)} />
                </div>
              </ArrayItem>
            ))}
            <Button type="button" onClick={addExperience}><Plus size={16}/> Add Experience</Button>
          </FormSection>

          {/* Educations */}
          <FormSection title="Education">
            {educations.map((edu, i) => (
              <ArrayItem key={edu.education_id || i} index={i} onRemove={removeEducation}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <Input label="Institute Name" name="institute_name" value={edu.institute_name} onChange={(e) => updateEducation(i, e)} required />
                  <Input label="Degree" name="degree" value={edu.degree} onChange={(e) => updateEducation(i, e)} required />
                  <Input label="Grade/GPA" type="number" step="0.1" name="grade" value={edu.grade} onChange={(e) => updateEducation(i, e)} required />
                  <Input label="Courses (comma separated)" name="courses" value={edu.courses} onChange={(e) => updateEducation(i, e)} />
                  <Input label="Start Date" type="date" name="start_date" value={edu.start_date} onChange={(e) => updateEducation(i, e)} />
                  <Input label="End Date" type="date" name="end_date" value={edu.end_date} onChange={(e) => updateEducation(i, e)} />
                </div>
              </ArrayItem>
            ))}
            <Button type="button" onClick={addEducation}><Plus size={16}/> Add Education</Button>
          </FormSection>

          {/* Projects */}
          <FormSection title="Projects">
            {projects.map((proj, i) => (
              <ArrayItem key={proj.project_id || i} index={i} onRemove={removeProject}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <Input label="Project Title" name="title" value={proj.title} onChange={(e) => updateProject(i, e)} required />
                  </div>
                  <Input label="GitHub URL" name="github_url" value={proj.github_url} onChange={(e) => updateProject(i, e)} />
                  <Input label="Deployed URL" name="deployed_url" value={proj.deployed_url} onChange={(e) => updateProject(i, e)} />
                  <div style={{ gridColumn: '1 / -1' }}>
                    <Input label="Skills Used (comma separated)" name="skills_used" value={proj.skills_used} onChange={(e) => updateProject(i, e)} required />
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <Input label="Description" name="description" value={proj.description} onChange={(e) => updateProject(i, e)} required />
                  </div>
                </div>
              </ArrayItem>
            ))}
            <Button type="button" onClick={addProject}><Plus size={16}/> Add Project</Button>
          </FormSection>

          {/* Leadership */}
          <FormSection title="Leadership">
            {leaderships.map((ld, i) => (
              <ArrayItem key={ld.leadership_id || i} index={i} onRemove={removeLeadership}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <Input label="Committee/Organization Name" name="committee_name" value={ld.committee_name} onChange={(e) => updateLeadership(i, e)} required />
                  <Input label="Position/Role" name="position" value={ld.position} onChange={(e) => updateLeadership(i, e)} required />
                  <Input label="Start Date" type="date" name="start_date" value={ld.start_date} onChange={(e) => updateLeadership(i, e)} />
                  <Input label="End Date" type="date" name="end_date" value={ld.end_date} onChange={(e) => updateLeadership(i, e)} />
                  <div style={{ gridColumn: '1 / -1' }}>
                    <Input label="Skills Used" name="skills_used" value={ld.skills_used} onChange={(e) => updateLeadership(i, e)} />
                  </div>
                </div>
              </ArrayItem>
            ))}
            <Button type="button" onClick={addLeadership}><Plus size={16}/> Add Leadership</Button>
          </FormSection>

          {/* Submit */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '32px' }}>
            <Button type="button" onClick={() => navigate('/dashboard')}>Skip / Cancel</Button>
            <Button type="submit" isLoading={isLoading}>Save Comprehensive Profile</Button>
          </div>
        </form>
      </Card>
      
    </div>
  );
};

export default Profile;
