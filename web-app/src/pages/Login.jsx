import React, { useState } from 'react';
import { api } from '../services/api';
import { Activity, LogIn, UserPlus, ShieldCheck, ArrowLeft, Sun, Moon, Eye, EyeOff } from 'lucide-react';

const Login = ({ onLogin, theme, toggleTheme }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPwd, setShowPwd]   = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  
  const [regData, setRegData] = useState({
    name: '', email: '', phone: '', birth: '', team: '', password: '', confirmPassword: ''
  });
  const [showRegPwd, setShowRegPwd] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError('');
    
    try {
      const res = await api.login(email, password);
      if (res && res.success) {
        onLogin(res.data, res.token);
      } else {
        setError(res?.message || 'Access Denied: Invalid credentials.');
      }
    } catch (err) {
      setError('Connection failed. Is the server running?');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError('');

    if (regData.password !== regData.confirmPassword) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }
    if (regData.password.length < 6) {
      setError('Password must be at least 6 characters.');
      setLoading(false);
      return;
    }
    
    try {
      const { confirmPassword, ...payload } = regData;
      const res = await api.register(payload);
      if (res && res.success) {
        setIsRegistering(false);
        setEmail(regData.email);
        setPassword('');
        setError('');
        alert('Registration successful! Please sign in.');
      } else {
        setError(res?.message || 'Registration failed.');
      }
    } catch (err) {
      setError('Connection failed during registration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-app)', position: 'relative' }}>
      <button
        onClick={toggleTheme}
        className="btn btn-ghost"
        style={{ position: 'absolute', top: '2rem', right: '2rem' }}
        type="button"
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>

      <div className="card" style={{ width: '100%', maxWidth: '420px', padding: '3rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', background: 'var(--primary)', padding: '0.75rem', borderRadius: '1rem', marginBottom: '1.5rem', boxShadow: '0 0 20px var(--primary-glow)' }}>
          <Activity size={32} color="white" />
        </div>
        
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          {isRegistering ? 'Create Account' : 'MazeRun Auth'}
        </h1>
        <p style={{ marginBottom: '2.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          {isRegistering ? 'Join the maze run system' : 'Sign in with your email and password'}
        </p>

        <div style={{ minHeight: '3rem' }}>
          {error && (
            <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-danger)', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              {error}
            </div>
          )}
        </div>

        {isRegistering ? (
          <form key="form-register" onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
            <input type="text"  placeholder="Full Name"      required value={regData.name}  onChange={e => setRegData({...regData, name: e.target.value})} />
            <input type="email" placeholder="Email Address"  required value={regData.email} onChange={e => setRegData({...regData, email: e.target.value})} />
            <input type="tel"   placeholder="Phone"          required value={regData.phone} onChange={e => setRegData({...regData, phone: e.target.value})} />
            <input type="date"  required value={regData.birth} onChange={e => setRegData({...regData, birth: e.target.value})} />
            <input type="number" placeholder="Team ID"       required value={regData.team}  onChange={e => setRegData({...regData, team: e.target.value})} />

            <div style={{ position: 'relative' }}>
              <input
                type={showRegPwd ? 'text' : 'password'}
                placeholder="Password (min. 6 chars)"
                required
                value={regData.password}
                onChange={e => setRegData({...regData, password: e.target.value})}
                style={{ width: '100%', paddingRight: '3rem' }}
              />
              <button
                type="button"
                onClick={() => setShowRegPwd(p => !p)}
                style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 0 }}
              >
                {showRegPwd ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            <input
              type={showRegPwd ? 'text' : 'password'}
              placeholder="Confirm Password"
              required
              value={regData.confirmPassword}
              onChange={e => setRegData({...regData, confirmPassword: e.target.value})}
            />
            
            <button type="submit" disabled={loading} className="btn btn-primary w-100" style={{ marginTop: '1rem' }}>
              <UserPlus size={20} /> <span>{loading ? 'Creating...' : 'Sign Up'}</span>
            </button>
            <button type="button" onClick={() => setIsRegistering(false)} className="btn btn-ghost w-100">
              <ArrowLeft size={16} /> <span>Back to Login</span>
            </button>
          </form>
        ) : (
          <form key="form-login" onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ textAlign: 'left' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginLeft: '0.5rem', marginBottom: '0.5rem', display: 'block' }}>Email</label>
              <input
                type="email"
                required
                placeholder="admin@mazerun.io"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: '100%', padding: '0.8rem 1rem' }}
              />
            </div>

            <div style={{ textAlign: 'left' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginLeft: '0.5rem', marginBottom: '0.5rem', display: 'block' }}>Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPwd ? 'text' : 'password'}
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ width: '100%', padding: '0.8rem 1rem', paddingRight: '3rem' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(p => !p)}
                  style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', padding: 0 }}
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary w-100" style={{ padding: '1rem' }}>
              <LogIn size={20} /> <span>{loading ? 'Authorizing...' : 'Sign In'}</span>
            </button>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', margin: '0.5rem 0' }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>NEW HERE?</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
            </div>

            <button type="button" onClick={() => setIsRegistering(true)} className="btn btn-ghost w-100">
              <span>Create an Account</span>
            </button>
          </form>
        )}

        <div style={{ marginTop: '2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
          <ShieldCheck size={14} /> <span>JWT Secured Session</span>
        </div>
      </div>
    </div>
  );
};

export default Login;
