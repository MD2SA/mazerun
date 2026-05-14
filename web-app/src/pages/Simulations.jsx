import React, { useState, useEffect } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar
} from 'recharts';
import { PlayCircle, Plus, ChevronRight, BarChart2, X, Users as UsersIcon } from 'lucide-react';

const SimulationDetails = ({ simulation, onClose }) => {
  const { theme } = useApp();
  const [data, setData] = useState({ temperature: [], sound: [], occupation: [] });
  const [loading, setLoading] = useState(true);

  const chartColors = {
    grid: theme === 'dark' ? '#27272a' : '#e4e4e7',
    text: theme === 'dark' ? '#71717a' : '#71717a',
    tooltipBg: theme === 'dark' ? '#18181b' : '#ffffff',
    tooltipBorder: theme === 'dark' ? '#27272a' : '#e4e4e7',
    tooltipText: theme === 'dark' ? '#fff' : '#000'
  };

  useEffect(() => {
    fetchData();
  }, [simulation.id]);

  const fetchData = async () => {
    const res = await api.getSensorData(simulation.id);
    if (res.success) setData(res.data);
    setLoading(false);
  };

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
                <XAxis dataKey="room" stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} label={{ value: 'Room', position: 'insideBottom', offset: -5, fill: chartColors.text }} />
                <YAxis stroke={chartColors.text} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  cursor={{ fill: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' }}
                  contentStyle={{ background: chartColors.tooltipBg, border: `1px solid ${chartColors.tooltipBorder}`, color: chartColors.tooltipText }}
                />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
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
  const [newSim, setNewSim] = useState({ description: '', team: user.team });

  useEffect(() => {
    fetchSims();
  }, [teamFilter]);

  const fetchSims = async () => {
    const res = await api.getSimulations(teamFilter);
    if (res.success) setSims(res.data);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    const res = await api.createSimulation({ ...newSim, email: user.email });
    if (res.success) {
      setShowCreate(false);
      fetchSims();
    } else {
      alert(res.message || 'Error creating simulation');
    }
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem' }}>Available Simulations</h2>
          <p className="text-secondary">Analysis of system runs and sensor logs</p>
        </div>
        {user.type === 'adm' && (
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus size={18} /> New Simulation
          </button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Description</th>
              <th>Team</th>
              <th>Date</th>
              <th>Data Points</th>
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
            <h2 style={{ marginBottom: '1.5rem' }}>{showCreate ? 'Create New Simulation' : 'Update Simulation'}</h2>
            <form onSubmit={showCreate ? handleCreate : handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
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
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Team ID</label>
                <input 
                  type="number" 
                  required 
                  value={showCreate ? newSim.team : editingSim.team}
                  onChange={(e) => showCreate ? setNewSim({ ...newSim, team: e.target.value }) : setEditingSim({ ...editingSim, team: e.target.value })}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => { setShowCreate(false); setEditingSim(null); }} className="btn btn-ghost flex-1">Cancel</button>
                <button type="submit" className="btn btn-primary flex-1">{showCreate ? 'Create' : 'Update'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Simulations;
