import React, { useState, useEffect } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { Terminal, Search, Filter } from 'lucide-react';

const Logs = () => {
  const { teamFilter } = useApp();
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000); // Live update
    return () => clearInterval(interval);
  }, [teamFilter]);

  const fetchLogs = async () => {
    const res = await api.getUnifiedLogs(null); // Filter by team logic inside SP or query
    if (res.success) setLogs(res.data);
    setLoading(false);
  };

  const filteredLogs = logs.filter(l => 
    l.type.toLowerCase().includes(filter.toLowerCase()) || 
    l.detail.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="card animate-fade" style={{ minHeight: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Terminal size={20} className="text-secondary" />
          <h2 style={{ fontSize: '1.1rem' }}>Unified Event Stream</h2>
        </div>
        <div style={{ position: 'relative', width: '300px' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
          <input 
            type="text" 
            placeholder="Search events, types, details..." 
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            style={{ width: '100%', paddingLeft: '2.5rem' }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', background: '#000', borderRadius: '0.5rem', padding: '1rem' }}>
        {loading ? (
          <div className="text-secondary">Connecting to event stream...</div>
        ) : filteredLogs.length > 0 ? (
          filteredLogs.map((log, i) => (
            <div key={i} className={`log-entry log-${log.type}`}>
              <span style={{ color: 'var(--text-secondary)', marginRight: '1rem' }}>[{new Date(log.time).toLocaleTimeString()}]</span>
              <span style={{ fontWeight: 600, marginRight: '1rem', display: 'inline-block', width: '80px' }}>{log.type}</span>
              <span>{log.detail}</span>
            </div>
          ))
        ) : (
          <div className="text-secondary" style={{ textAlign: 'center', padding: '2rem' }}>No events detected in the current window.</div>
        )}
      </div>
    </div>
  );
};

export default Logs;
