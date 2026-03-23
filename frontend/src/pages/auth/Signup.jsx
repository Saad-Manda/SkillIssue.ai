import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';

export const Signup = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState(null);
  const { signup, setToken, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await signup(formData);
      // Backend returns access_token and signup_token
      setToken(response.access_token);
      localStorage.setItem('signup_token', response.signup_token);
      navigate('/profile/new'); // Must create profile immediately
    } catch (err) {
      setError(err.message || 'Signup failed');
    }
  };

  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <Card title="Create an account" subtitle="Join SkillIssue.ai to practice interviewing">
        {error && (
          <div style={{ padding: '12px', backgroundColor: '#FEF2F2', color: '#EF4444', borderRadius: '6px', marginBottom: '16px', fontSize: '14px' }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <Input 
            label="Username" 
            name="username"
            type="text" 
            placeholder="johndoe" 
            value={formData.username}
            onChange={handleChange}
            required
          />
          <Input 
            label="Email Address" 
            name="email"
            type="email" 
            placeholder="you@company.com" 
            value={formData.email}
            onChange={handleChange}
            required
          />
          <Input 
            label="Password" 
            name="password"
            type="password" 
            placeholder="••••••••" 
            value={formData.password}
            onChange={handleChange}
            required
            minLength={8}
          />
          <div style={{ marginTop: '24px' }}>
            <Button type="submit" fullWidth isLoading={isLoading}>
              Create Account
            </Button>
          </div>
        </form>
        <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '14px', color: 'var(--text-secondary)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>Sign in</Link>
        </p>
      </Card>
    </div>
  );
};

export default Signup;
