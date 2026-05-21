import React, { useState, useEffect } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { Activity, AlertTriangle, TrendingUp, Cpu, Clock, Volume2, Users } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color }) => (
  <div className="card stat-card animate-fade">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div>
        <h3>{title}</h3>
        <div className="value">{value}</div>
      </div>
      <div style={{ padding: '0.6rem', borderRadius: '0.5rem', background: `${color}15`, color: color }}>
        <Icon size={20} />
      </div>
    </div>
  </div>
);

const Overview = () => {
  const { teamFilter } = useApp();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [teamFilter]);

  const fetchData = async () => {
    setLoading(true);
    const [statsRes, logsRes] = await Promise.all([
      api.getAnalytics(teamFilter),
      api.getUnifiedLogs(null, 10, teamFilter)
    ]);

    if (statsRes.success) setStats(statsRes.data);
    if (logsRes.success) setActivity(logsRes.data);
    setLoading(false);
  };

  if (loading && !stats) return <div className="text-secondary">Crunching system data...</div>;

  return (
    <div className="animate-fade">
      <div className="stat-grid">
        <StatCard title="Total Simulations" value={stats?.total_sims || 0} icon={Cpu} color="#3b82f6" />
        <StatCard title="Processed Events" value={stats?.total_measures || 0} icon={TrendingUp} color="#10b981" />
        <StatCard title="System Alerts" value={stats?.total_alerts || 0} icon={AlertTriangle} color="#ef4444" />
        <StatCard title="Total Marsamis" value={stats?.total_marsamis || 0} icon={Users} color="#8b5cf6" />
        <StatCard title="Avg Temperature" value={`${stats?.avg_temp || 0}°C`} icon={Activity} color="#f59e0b" />
        <StatCard title="Avg Sound" value={`${stats?.avg_sound || 0} dB`} icon={Volume2} color="#ec4899" />
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Clock size={18} className="text-secondary" /> Recent System Activity
          </h2>
        </div>
        <table className="table" style={{ margin: 0 }}>
          <thead>
            <tr>
              <th>Time</th>
              <th>Type</th>
              <th>Detail</th>
            </tr>
          </thead>
          <tbody>
            {activity.map((log, i) => (
              <tr key={i}>
                <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{new Date(log.time).toLocaleTimeString()}</td>
                <td>
                  <span className={`badge log-${log.type}`} style={{ fontSize: '0.7rem' }}>{log.type}</span>
                </td>
                <td style={{ fontWeight: 500 }}>
                  {log.detail}
                </td>
              </tr>
            ))}
            {activity.length === 0 && (
              <tr>
                <td colSpan="3" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>No recent activity found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Overview;
