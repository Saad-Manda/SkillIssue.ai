import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';

export const Login = () => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState(null);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await login(formData.username, formData.email, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  };

  const handleChange = (e) => setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
      <Card title="Welcome back" subtitle="Sign in to your SkillIssue.ai account">
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
          />
          <div style={{ marginTop: '24px' }}>
            <Button type="submit" fullWidth isLoading={isLoading}>
              Sign In
            </Button>
          </div>
        </form>
        <p style={{ textAlign: 'center', marginTop: '24px', fontSize: '14px', color: 'var(--text-secondary)' }}>
          Don't have an account? <Link to="/signup" style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>Sign up</Link>
        </p>
      </Card>
    </div>
  );
};

export default Login;
