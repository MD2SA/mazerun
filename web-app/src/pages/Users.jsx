import React, { useState, useEffect } from 'react';
import { useApp } from '../App';
import { api } from '../services/api';
import { UserPlus, Trash2, Shield, User as UserIcon, X } from 'lucide-react';

const Users = () => {
  const { user: currentUser } = useApp();
  const [users, setUsers] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ name: '', email: '', phone: '', birth: '', team: '', type: 'usr' });
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    const res = await api.getUsers();
    if (res.success) {
      const allUsers = res.data || [];
      // RBAC: usr only sees themselves
      if (currentUser.type === 'usr') {
        setUsers(allUsers.filter(u => u.email === currentUser.email));
      } else {
        setUsers(allUsers);
      }
    }
    setLoading(false);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    const res = await api.createUser(formData);
    if (res.success) {
      setShowCreate(false);
      fetchUsers();
      setFormData({ name: '', email: '', phone: '', birth: '', team: '', type: 'usr' });
    } else {
      alert(res.message || 'Error creating user');
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    const res = await api.updateUser(formData);
    if (res.success) {
      setEditingUser(null);
      fetchUsers();
      setFormData({ name: '', email: '', phone: '', birth: '', team: '', type: 'usr' });
    } else {
      alert(res.message || 'Error updating user');
    }
  };

  const openEdit = (u) => {
    setEditingUser(u);
    setFormData({ ...u });
  };

  const handleDelete = async (email) => {
    if (window.confirm(`Permanently remove access for ${email}?`)) {
      const res = await api.deleteUser(email);
      if (res.success) fetchUsers();
    }
  };

  return (
    <div className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem' }}>System Directory</h2>
          <p className="text-secondary">Manage access control and team assignments</p>
        </div>
        {currentUser.type === 'adm' && (
          <button onClick={() => { setFormData({ name: '', email: '', phone: '', birth: '', team: '', type: 'usr' }); setShowCreate(true); }} className="btn btn-primary">
            <UserPlus size={18} /> Register User
          </button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table className="table">
          <thead>
            <tr>
              <th>Identity</th>
              <th>Contacts</th>
              <th>Team Context</th>
              <th>Role</th>
              <th style={{ textAlign: 'right' }}>Management</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.email}>
                <td>
                  <div className="d-flex align-items-center gap-3">
                    <div style={{ width: '36px', height: '36px', background: 'var(--bg-input)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <UserIcon size={18} className="text-secondary" />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600 }}>{u.name}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{u.email}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div style={{ fontSize: '0.85rem' }}>{u.phone}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Born: {u.birth}</div>
                </td>
                <td>
                  <span className="badge badge-usr">{u.team ? `TEAM ${u.team}` : 'N/A'}</span>
                </td>
                <td>
                  <span className={`badge badge-${u.type.toLowerCase()}`}>{u.type}</span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <div className="d-flex justify-content-end gap-2">
                    <button
                      onClick={() => openEdit(u)}
                      className="btn btn-ghost"
                      style={{ padding: '0.4rem' }}
                    >
                      <Shield size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(u.email)}
                      className="btn btn-ghost"
                      style={{ color: 'var(--accent-danger)', padding: '0.4rem' }}
                      disabled={u.email === currentUser.email}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(showCreate || editingUser) && (
        <div className="modal-overlay">
          <div className="card modal-content animate-fade" style={{ maxWidth: '500px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.2rem' }}>{showCreate ? 'Register New Entity' : 'Update Entity'}</h2>
              <button onClick={() => { setShowCreate(false); setEditingUser(null); }} className="btn btn-ghost"><X size={20} /></button>
            </div>
            <form onSubmit={showCreate ? handleCreate : handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <input type="text" placeholder="Full Name" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              <input type="email" placeholder="Email Address" required disabled={!!editingUser} value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
              <input type="tel" placeholder="Phone Number" required value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
              <input type="date" placeholder="Birth Date" required value={formData.birth} onChange={e => setFormData({...formData, birth: e.target.value})} />
              <div className="d-flex gap-2">
                <input
                  type="number"
                  placeholder="Team ID"
                  required={formData.type === 'usr'}
                  disabled={formData.type === 'adm'}
                  value={formData.type === 'adm' ? '' : formData.team}
                  onChange={e => setFormData({...formData, team: e.target.value})}
                  className="flex-1"
                />
                <select
                  value={formData.type}
                  onChange={e => setFormData({...formData, type: e.target.value})}
                  className="flex-1"
                  disabled={editingUser && editingUser.email === currentUser.email}
                >
                  <option value="usr">User (USR)</option>
                  <option value="adm">Admin (ADM)</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary w-100" style={{ marginTop: '1rem' }}>
                {showCreate ? 'Authorize User' : 'Update User'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
