import React, { useState, useEffect, useCallback } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { Terminal, Search, Filter, ChevronDown } from 'lucide-react';

const Logs = () => {
  const { teamFilter } = useApp();
  const [logs, setLogs] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [selectedSim, setSelectedSim] = useState('');
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const LIMIT = 50;

  const fetchSimulations = useCallback(async () => {
    const res = await api.getSimulations(teamFilter);
    if (res.success) setSimulations(res.data);
  }, [teamFilter]);

  const fetchLogs = useCallback(async (currentOffset = 0, append = false) => {
    if (!append) setLoading(true);
    else setLoadingMore(true);

    const res = await api.getUnifiedLogs(
      selectedSim || null,
      LIMIT,
      teamFilter,
      currentOffset
    );

    if (res.success) {
      if (append) {
        setLogs(prev => [...prev, ...res.data]);
      } else {
        setLogs(res.data);
      }
      setHasMore(res.data.length === LIMIT);
    }

    setLoading(false);
    setLoadingMore(false);
  }, [selectedSim, teamFilter]);

  useEffect(() => {
    fetchSimulations();
  }, [fetchSimulations]);

  useEffect(() => {
    setOffset(0);
    fetchLogs(0, false);

    // Live update only if on first page and no specific simulation filter (optional preference)
    // For now, let's keep live update for the first page only
    const interval = setInterval(() => {
      if (offset === 0) {
        fetchLogs(0, false);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchLogs, selectedSim, teamFilter]);

  const handleLoadMore = () => {
    const nextOffset = offset + LIMIT;
    setOffset(nextOffset);
    fetchLogs(nextOffset, true);
  };

  const filteredLogs = logs.filter(l => 
    l.type.toLowerCase().includes(filter.toLowerCase()) || 
    l.detail.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="card animate-fade" style={{ minHeight: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Terminal size={20} className="text-secondary" />
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, letterSpacing: '-0.01em' }}>Unified Event Stream</h2>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', width: '220px' }}>
            <Filter size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', pointerEvents: 'none' }} />
            <select
              value={selectedSim}
              onChange={(e) => setSelectedSim(e.target.value)}
              style={{
                width: '100%',
                paddingLeft: '2.5rem',
                appearance: 'none',
                fontSize: '0.85rem'
              }}
              className="input"
            >
              <option value="">All Simulations</option>
              {simulations.map(sim => (
                <option key={sim.id} value={sim.id}>
                  Simulation #{sim.id} - {sim.description.substring(0, 15)}...
                </option>
              ))}
            </select>
            <ChevronDown size={14} style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', pointerEvents: 'none' }} />
          </div>

          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input
              type="text"
              placeholder="Search logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{ width: '100%', paddingLeft: '2.5rem', fontSize: '0.85rem' }}
              className="input"
            />
          </div>
        </div>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        background: '#000',
        borderRadius: '0.75rem',
        padding: '1.25rem',
        border: '1px solid var(--border)',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: '0.85rem',
        lineHeight: '1.5'
      }}>
        {loading && logs.length === 0 ? (
          <div className="text-secondary animate-pulse">Connecting to event stream...</div>
        ) : filteredLogs.length > 0 ? (
          <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {filteredLogs.map((log, i) => (
                <div key={i} className={`log-entry log-${log.type}`} style={{ display: 'flex', alignItems: 'flex-start' }}>
                  <span style={{ color: 'var(--text-secondary)', marginRight: '1rem', whiteSpace: 'nowrap', opacity: 0.7 }}>
                    [{new Date(log.time).toLocaleTimeString()}]
                  </span>
                  <span style={{
                    fontWeight: 700,
                    marginRight: '1rem',
                    display: 'inline-block',
                    width: '75px',
                    fontSize: '0.75rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {log.type}
                  </span>
                  <span style={{ color: '#e4e4e7' }}>{log.detail}</span>
                </div>
              ))}
            </div>

            {hasMore && (
              <div style={{ marginTop: '2rem', textAlign: 'center' }}>
                <button
                  onClick={handleLoadMore}
                  disabled={loadingMore}
                  className="btn btn-ghost"
                  style={{
                    fontSize: '0.8rem',
                    padding: '0.5rem 1.5rem',
                    color: 'var(--text-secondary)',
                    border: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  {loadingMore ? 'Loading...' : 'Load older events'}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-secondary" style={{ textAlign: 'center', padding: '3rem' }}>
            No events detected in the current filter.
          </div>
        )}
      </div>
    </div>
  );
};

export default Logs;
