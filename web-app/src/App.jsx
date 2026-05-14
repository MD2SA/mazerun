import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users as UsersIcon, History, PlayCircle, LogOut,
  Settings, Filter, ChevronDown, Activity, Globe, Sun, Moon
} from 'lucide-react';

import Login from './pages/Login';
import Overview from './pages/Overview';
import Users from './pages/Users';
import Simulations from './pages/Simulations';
import Logs from './pages/Logs';

// Context for global state
const AppContext = createContext();
export const useApp = () => useContext(AppContext);

const Sidebar = ({ user, onLogout, theme }) => {
  const location = useLocation();
  const menu = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Simulations', path: '/simulations', icon: PlayCircle },
    { name: 'Users', path: '/users', icon: UsersIcon },
    { name: 'System Logs', path: '/logs', icon: History },
  ];

  return (
    <aside className="sidebar">
      <div style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ background: 'var(--primary)', padding: '0.4rem', borderRadius: '0.4rem' }}>
          <Activity size={20} color="white" />
        </div>
        <span style={{ fontWeight: 700, fontSize: '1.2rem', letterSpacing: '-0.02em' }}>MAZERUN</span>
      </div>

      <nav style={{ flex: 1, padding: '0 1rem' }}>
        {menu.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`btn btn-ghost w-100 ${location.pathname === item.path ? 'active' : ''}`}
            style={{ justifyContent: 'flex-start', marginBottom: '0.25rem', color: location.pathname === item.path ? (theme === 'dark' ? 'white' : 'var(--primary)') : 'var(--text-secondary)' }}
          >
            <item.icon size={18} /> {item.name}
          </Link>
        ))}
      </nav>

      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)' }}>
        <div style={{ marginBottom: '2rem' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Logged in as</p>
          <p style={{ fontWeight: 600, fontSize: '0.85rem' }}>{user.email}</p>
          <span className={`badge badge-${user.type.toLowerCase()}`} style={{ marginTop: '0.4rem', display: 'inline-block' }}>
            {user.type}
          </span>
        </div>
        <button onClick={onLogout} className="btn btn-ghost w-100" style={{ color: 'var(--accent-danger)' }}>
          <LogOut size={18} /> Sign Out
        </button>
      </div>
    </aside>
  );
};

const Header = ({ user, teamFilter, setTeamFilter, theme, toggleTheme }) => {
  return (
    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>{document.title || 'Dashboard'}</h1>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        {user.type === 'adm' && (
          <div className="d-flex align-items-center gap-2">
            <Globe size={16} color="var(--text-secondary)" />
            <select
              value={teamFilter || ''}
              onChange={(e) => setTeamFilter(e.target.value || null)}
              style={{ background: 'var(--bg-card)', fontSize: '0.85rem' }}
            >
              <option value="">All Teams</option>
              {[1, 2, 3, 10, 20, 25, 30].map(t => <option key={t} value={t}>Team {t}</option>)}
            </select>
          </div>
        )}
        <div style={{ padding: '0.5rem 1rem', background: 'var(--bg-card)', borderRadius: '0.5rem', border: '1px solid var(--border)', fontSize: '0.85rem' }}>
          Context: <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{teamFilter ? `Team ${teamFilter}` : 'Global'}</span>
        </div>
        <button
          onClick={toggleTheme}
          className="btn btn-ghost"
          style={{ padding: '0.5rem' }}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  );
};

const App = () => {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user')));
  const [teamFilter, setTeamFilter] = useState(null);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  useEffect(() => {
    if (user && user.type !== 'adm') {
      setTeamFilter(user.team);
    }
  }, [user]);

  const handleLogin = (data) => {
    setUser(data);
    localStorage.setItem('user', JSON.stringify(data));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (!user) return <Login onLogin={handleLogin} theme={theme} toggleTheme={toggleTheme} />;

  return (
    <AppContext.Provider value={{ user, teamFilter, setTeamFilter, theme, toggleTheme }}>
      <Router>
        <div className="app-container">
          <Sidebar user={user} onLogout={handleLogout} theme={theme} toggleTheme={toggleTheme} />
          <main className="main-content">
            <Header user={user} teamFilter={teamFilter} setTeamFilter={setTeamFilter} theme={theme} toggleTheme={toggleTheme} />
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/simulations" element={<Simulations />} />
              <Route path="/users" element={<Users />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AppContext.Provider>
  );
};

export default App;
