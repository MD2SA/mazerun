import { useState, useEffect, useCallback } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar
} from 'recharts';
import { PlayCircle, Plus, BarChart2, X } from 'lucide-react';

const SimulationDetails = ({ simulation, onClose }) => {
  const { theme } = useApp();
  const [data, setData] = useState({ temperature: [], sound: [], occupation: [] });

  const chartColors = {
    grid: theme === 'dark' ? '#27272a' : '#e4e4e7',
    text: theme === 'dark' ? '#71717a' : '#71717a',
    tooltipBg: theme === 'dark' ? '#18181b' : '#ffffff',
    tooltipBorder: theme === 'dark' ? '#27272a' : '#e4e4e7',
    tooltipText: theme === 'dark' ? '#fff' : '#000'
  };

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      const res = await api.getSensorData(simulation.id);
      if (!cancelled && res.success) setData(res.data);
    };

    fetchData();
    const refreshInterval = setInterval(fetchData, 2000);

    return () => {
      cancelled = true;
      clearInterval(refreshInterval);
    };
  }, [simulation.id]);

  return (
    <div className="modal-overlay">
      <div className="glass-card modal-content" style={{ maxWidth: '1000px', width: '95%', maxHeight: '90vh', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem' }}>{simulation.description}</h2>
            <p className="text-secondary">Simulation ID: {simulation.id} | Team {simulation.team}</p>
          </div>
          <button onClick={onClose} className="btn btn-ghost"><X size={24} /></button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <div className="card">
            <h3 style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>Temperature Trends (°C)</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.temperature}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                  <XAxis dataKey="time" hide />
                  <YAxis stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: chartColors.tooltipBg, border: `1px solid ${chartColors.tooltipBorder}`, color: chartColors.tooltipText }} />
                  <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>Sound Levels (dB)</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.sound}>
                  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                  <XAxis dataKey="time" hide />
                  <YAxis stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ background: chartColors.tooltipBg, border: `1px solid ${chartColors.tooltipBorder}`, color: chartColors.tooltipText }} />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '1rem', marginBottom: '1.5rem' }}>Room Occupation (Marsamis)</h3>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.occupation}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                <XAxis dataKey="room" stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} label={{ value: 'Room ID', position: 'insideBottom', offset: -5, fill: chartColors.text, fontSize: 10 }} />
                <YAxis stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}
                  contentStyle={{ background: chartColors.tooltipBg, border: `1px solid ${chartColors.tooltipBorder}`, color: chartColors.tooltipText }}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="odd" name="Odd Marsamis" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                <Bar dataKey="even" name="Even Marsamis" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

const Simulations = () => {
  const { teamFilter, user } = useApp();
  const [sims, setSims] = useState([]);
  const [selectedSim, setSelectedSim] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [editingSim, setEditingSim] = useState(null);
  const [newSim, setNewSim] = useState({ description: '', team: user.team || '', owner_email: user.email || '', number_marsamis: 30 });
  const [createStatus, setCreateStatus] = useState(null);
  const [pageStatus, setPageStatus] = useState(null);
  const [creating, setCreating] = useState(false);

  const fetchSims = useCallback(async () => {
    const res = await api.getSimulations(teamFilter);
    if (res.success) setSims(res.data);
  }, [teamFilter]);

  useEffect(() => {
    let cancelled = false;

    const loadSims = async () => {
      const res = await api.getSimulations(teamFilter);
      if (!cancelled && res.success) setSims(res.data);
    };

    loadSims();

    return () => {
      cancelled = true;
    };
  }, [teamFilter]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateStatus(null);

    const res = await api.createSimulation({
      description: newSim.description.trim(),
      number_marsamis: Number(newSim.number_marsamis),
      ...(user.type === 'adm' ? {
        team: Number(newSim.team),
        owner_email: newSim.owner_email.trim(),
      } : {}),
    });

    if (res.success) {
      setPageStatus({
        type: 'success',
        message: res.message || 'Simulation created and started successfully',
      });
      setShowCreate(false);
      setNewSim({ description: '', team: user.team || '', owner_email: user.email || '', number_marsamis: 30 });
      fetchSims();
    } else {
      setCreateStatus({
        type: 'error',
        message: res.message || 'Error creating simulation',
      });
    }

    setCreating(false);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    const res = await api.updateSimulation(editingSim);
    if (res.success) {
      setEditingSim(null);
      fetchSims();
    } else {
      alert(res.message || 'Error updating simulation');
    }
  };

  return (
    <div className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem' }}>Available Simulations</h2>
          <p className="text-secondary">Analysis of system runs and sensor logs</p>
        </div>
        <button onClick={() => { setCreateStatus(null); setPageStatus(null); setShowCreate(true); }} className="btn btn-primary" style={{ fontSize: '0.95rem', padding: '0.8rem 1.2rem' }}>
          <PlayCircle size={20} /> Create and Start Simulation
        </button>
      </div>

      {pageStatus && (
        <div
          style={{
            padding: '0.85rem 1rem',
            borderRadius: '0.5rem',
            border: `1px solid ${pageStatus.type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)'}`,
            color: pageStatus.type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)',
            background: pageStatus.type === 'success' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
            fontSize: '0.9rem',
            marginBottom: '1rem',
          }}
        >
          {pageStatus.message}
        </div>
      )}

      <div className="card" style={{ padding: 0 }}>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Description</th>
              <th>Team</th>
              <th>Date</th>
              <th>Data Points</th>
              <th>Total Score</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sims.map(sim => (
              <tr key={sim.id}>
                <td style={{ color: 'var(--text-secondary)' }}>#{sim.id}</td>
                <td style={{ fontWeight: 500 }}>{sim.description}</td>
                <td><span className="badge badge-usr">T{sim.team}</span></td>
                <td style={{ color: 'var(--text-secondary)' }}>{new Date(sim.startDate).toLocaleString()}</td>
                <td>{sim.measures}</td>
                <td>{sim.total_score ?? '-'}</td>
                <td style={{ textAlign: 'right' }}>
                  <div className="d-flex justify-content-end gap-2">
                    <button onClick={() => setSelectedSim(sim)} className="btn btn-ghost" style={{ padding: '0.4rem' }}>
                      <BarChart2 size={18} />
                    </button>
                    {user.type === 'adm' && (
                      <button onClick={() => setEditingSim(sim)} className="btn btn-ghost" style={{ padding: '0.4rem' }}>
                        <Plus size={18} style={{ transform: 'rotate(45deg)' }} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedSim && <SimulationDetails simulation={selectedSim} onClose={() => setSelectedSim(null)} />}

      {(showCreate || editingSim) && (
        <div className="modal-overlay">
          <div className="card modal-content animate-fade">
            <h2 style={{ marginBottom: '1.5rem' }}>{showCreate ? 'Start New Simulation' : 'Update Simulation'}</h2>
            <form onSubmit={showCreate ? handleCreate : handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {showCreate && createStatus && (
                <div
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '0.5rem',
                    border: `1px solid ${createStatus.type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)'}`,
                    color: createStatus.type === 'success' ? 'var(--accent-success)' : 'var(--accent-danger)',
                    background: createStatus.type === 'success' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                    fontSize: '0.9rem',
                  }}
                >
                  {createStatus.message}
                </div>
              )}
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Description</label>
                <input 
                  type="text" 
                  required 
                  value={showCreate ? newSim.description : editingSim.description}
                  onChange={(e) => showCreate ? setNewSim({ ...newSim, description: e.target.value }) : setEditingSim({ ...editingSim, description: e.target.value })}
                  placeholder="e.g. Test Run with Room A sensors"
                  style={{ width: '100%' }}
                />
              </div>
              {showCreate && (
                <div className="input-group">
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Number of Marsamis</label>
                  <input
                    type="number"
                    required
                    min="1"
                    max="100"
                    value={newSim.number_marsamis}
                    onChange={(e) => setNewSim({ ...newSim, number_marsamis: e.target.value })}
                    style={{ width: '100%' }}
                  />
                </div>
              )}
              {showCreate ? (
                <>
                  {user.type === 'adm' && (
                    <>
                      <div className="input-group">
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Team ID</label>
                        <input
                          type="number"
                          required
                          min="1"
                          value={newSim.team}
                          onChange={(e) => setNewSim({ ...newSim, team: e.target.value })}
                          style={{ width: '100%' }}
                        />
                      </div>
                      <div className="input-group">
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Owner Email</label>
                        <input
                          type="email"
                          required
                          value={newSim.owner_email}
                          onChange={(e) => setNewSim({ ...newSim, owner_email: e.target.value })}
                          placeholder="user@example.com"
                          style={{ width: '100%' }}
                        />
                      </div>
                    </>
                  )}
                </>
              ) : (
                <div className="input-group">
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Team ID</label>
                  <input 
                    type="number" 
                    required 
                    value={editingSim.team}
                    onChange={(e) => setEditingSim({ ...editingSim, team: e.target.value })}
                    style={{ width: '100%' }}
                  />
                </div>
              )}
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => { setShowCreate(false); setEditingSim(null); setCreateStatus(null); }}
                  className="btn btn-ghost flex-1"
                  disabled={creating}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary flex-1" disabled={creating}>
                  {showCreate ? (creating ? 'Starting...' : 'Start') : 'Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulations;
