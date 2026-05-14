import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Plus, Edit2, Play, Calendar, Users as UsersIcon } from 'lucide-react';

const Dashboard = ({ user }) => {
  const [simulations, setSimulations] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingSim, setEditingSim] = useState(null);
  const [formData, setFormData] = useState({ description: '', team: user.team });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    setLoading(true);
    setError('');
    try {
      const res = user.type === 'ADM' ? await api.getAllSimulations() : await api.getUserSimulations(user.email);
      if (res.success) {
        setSimulations(res.data || []);
      } else {
        setError(res.message || 'Failed to load simulations');
      }
    } catch (err) {
      setError('Network error. Check if backend is running.');
    }
    setLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = editingSim 
      ? await api.updateSimulation({ id: editingSim.id, description: formData.description })
      : await api.createSimulation({ ...formData, email: user.email });
    
    if (res.success) {
      setShowModal(false);
      setEditingSim(null);
      setFormData({ description: '', team: user.team });
      fetchSimulations();
    }
  };

  const openEdit = (sim) => {
    setEditingSim(sim);
    setFormData({ description: sim.description, team: sim.team });
    setShowModal(true);
  };

  return (
    <div className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Simulations</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage and monitor your maze simulations</p>
        </div>
        <button onClick={() => { setEditingSim(null); setFormData({ description: '', team: user.team }); setShowModal(true); }} className="btn-primary">
          <Plus size={20} /> New Simulation
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '1rem', borderRadius: '0.75rem', marginBottom: '1.5rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>Loading simulations...</div>
      ) : simulations.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
          {simulations.map(sim => (
            <div key={sim.id} className="glass-card" style={{ padding: '1.5rem', transition: 'transform 0.2s' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', padding: '0.5rem', borderRadius: '0.5rem', fontSize: '0.8rem', fontWeight: '600' }}>
                  ID: #{sim.id}
                </div>
                <button onClick={() => openEdit(sim)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                  <Edit2 size={18} />
                </button>
              </div>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>{sim.description}</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent)', padding: '0.75rem', borderRadius: '0.75rem', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Measures</p>
                  <p style={{ fontSize: '1.2rem', fontWeight: '700' }}>{sim.total_measures || 0}</p>
                </div>
                <div style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', padding: '0.75rem', borderRadius: '0.75rem', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Messages</p>
                  <p style={{ fontSize: '1.2rem', fontWeight: '700' }}>{sim.total_messages || 0}</p>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <UsersIcon size={16} /> Team: {sim.team}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Calendar size={16} /> {new Date(sim.startDate).toLocaleDateString()}
                </div>
                {user.type === 'ADM' && (
                  <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '0.5rem' }}>
                    Owner: {sim.user_email || 'System'}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>No simulations found.</p>
          <button onClick={() => setShowModal(true)} className="btn-secondary">Create your first one</button>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="glass-card modal-content">
            <h2 style={{ marginBottom: '1.5rem' }}>{editingSim ? 'Edit Simulation' : 'New Simulation'}</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Description</label>
                <textarea 
                  required 
                  rows="3"
                  value={formData.description} 
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  placeholder="e.g., Performance test with 25 Marsamis"
                  style={{ width: '100%', resize: 'none' }}
                />
              </div>
              <div className="input-group">
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Team ID</label>
                <input 
                  type="number" 
                  required 
                  disabled={!!editingSim}
                  value={formData.team} 
                  onChange={e => setFormData({...formData, team: e.target.value})}
                  style={{ width: '100%' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary" style={{ flex: 1 }}>Cancel</button>
                <button type="submit" className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
                  {editingSim ? 'Save Changes' : 'Start Simulation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
