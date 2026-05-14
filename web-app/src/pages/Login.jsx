import React, { useState } from 'react';
import { api } from '../services/api';
import { Activity, LogIn, UserPlus, ShieldCheck, ArrowLeft, Sun, Moon } from 'lucide-react';

const Login = ({ onLogin, theme, toggleTheme }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [regData, setRegData] = useState({
    name: '', email: '', phone: '', birth: '', team: ''
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const res = await api.login(email);
    if (res.success) {
      onLogin(res.data);
    } else {
      setError('Access Denied: Invalid credentials or entity not found.');
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const res = await api.register(regData);
    if (res.success) {
      setIsRegistering(false);
      setEmail(regData.email);
      alert('Registration successful! Please sign in.');
    } else {
      setError(res.message || 'Registration failed.');
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-app)', position: 'relative' }}>
      <button
        onClick={toggleTheme}
        className="btn btn-ghost"
        style={{ position: 'absolute', top: '2rem', right: '2rem' }}
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>

      <div className="card animate-fade" style={{ width: '100%', maxWidth: '400px', padding: '3rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', background: 'var(--primary)', padding: '0.75rem', borderRadius: '1rem', marginBottom: '1.5rem', boxShadow: '0 0 20px var(--primary-glow)' }}>
          <Activity size={32} color="white" />
        </div>
        
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          {isRegistering ? 'Create Account' : 'MazeRun Auth'}
        </h1>
        <p className="text-secondary" style={{ marginBottom: '2.5rem', fontSize: '0.9rem' }}>
          {isRegistering ? 'Join the maze run system' : 'Enter your authorized email to proceed'}
        </p>

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-danger)', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            {error}
          </div>
        )}

        {isRegistering ? (
          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
            <input type="text" placeholder="Full Name" required value={regData.name} onChange={e => setRegData({...regData, name: e.target.value})} />
            <input type="email" placeholder="Email Address" required value={regData.email} onChange={e => setRegData({...regData, email: e.target.value})} />
            <input type="tel" placeholder="Phone" required value={regData.phone} onChange={e => setRegData({...regData, phone: e.target.value})} />
            <input type="date" required value={regData.birth} onChange={e => setRegData({...regData, birth: e.target.value})} />
            <input type="number" placeholder="Team ID" required value={regData.team} onChange={e => setRegData({...regData, team: e.target.value})} />
            
            <button type="submit" disabled={loading} className="btn btn-primary w-100" style={{ marginTop: '1rem' }}>
              <UserPlus size={20} /> {loading ? 'Creating...' : 'Sign Up'}
            </button>
            <button type="button" onClick={() => setIsRegistering(false)} className="btn btn-ghost w-100">
              <ArrowLeft size={16} /> Back to Login
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ textAlign: 'left' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginLeft: '0.5rem', marginBottom: '0.5rem', display: 'block' }}>Email Identity</label>
              <input 
                type="email" 
                required 
                placeholder="admin@mazerun.io" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: '100%', padding: '0.8rem 1rem' }}
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary w-100" style={{ padding: '1rem' }}>
              <LogIn size={20} /> {loading ? 'Authorizing...' : 'Sign In'}
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '0.5rem 0' }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>NEW HERE?</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
            </div>

            <button type="button" onClick={() => setIsRegistering(true)} className="btn btn-ghost w-100">
              Create an Account
            </button>
          </form>
        )}

        <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
          <ShieldCheck size={14} /> Encrypted Session Management
        </div>
      </div>
    </div>
  );
};

export default Login;
