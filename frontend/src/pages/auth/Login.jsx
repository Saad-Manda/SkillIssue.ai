import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const SunIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="4"/>
    <path d="M12 2v2"/><path d="M12 20v2"/>
    <path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>
    <path d="M2 12h2"/><path d="M20 12h2"/>
    <path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>
  </svg>
);

const MoonIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
  </svg>
);

export const Login = () => {
  const [theme, setTheme] = useState('dark');
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState(null);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

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
    <div className={`auth-wrapper ${theme === 'dark' ? 'theme-dark' : 'theme-light'}`}>
      <button 
        className="theme-toggle-btn" 
        onClick={toggleTheme} 
        aria-label="Toggle Theme"
      >
        {theme === 'light' ? <MoonIcon /> : <SunIcon />}
      </button>

      <div className="auth-card">
        <div className="auth-card-content">
          <div className="auth-header">
            <h1>Welcome back</h1>
            <p>Sign in to your SkillIssue.ai account</p>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input 
                id="username"
                name="username"
                type="text" 
                placeholder="johndoe" 
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input 
                id="email"
                name="email"
                type="email" 
                placeholder="you@company.com" 
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input 
                id="password"
                name="password"
                type="password" 
                placeholder="••••••••" 
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
        </div>
        
        <div className="auth-footer">
          <p>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
