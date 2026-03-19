import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, User, LayoutDashboard } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '16px 32px',
      backgroundColor: 'var(--bg-primary)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 10
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
        <Link to="/dashboard" style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-primary)' }}>
          SkillIssue.ai
        </Link>
        <div style={{ display: 'flex', gap: '24px' }}>
          <Link to="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '15px' }}>
            <LayoutDashboard size={18} /> Dashboard
          </Link>
          <Link to="/profile" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '15px' }}>
            <User size={18} /> Profile
          </Link>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          {user?.email || 'User'}
        </span>
        <button 
          onClick={handleLogout}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            backgroundColor: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          <LogOut size={16} /> Logout
        </button>
      </div>
    </nav>
  );
};
