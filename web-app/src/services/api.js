const API_URL = 'http://127.0.0.1:8000/web/api.php';

async function request(action, params = {}, data = null) {
  const url = new URL(API_URL);
  url.searchParams.append('action', action);
  
  // Always include requester_email if available in localStorage
  const user = JSON.parse(localStorage.getItem('user'));
  if (user && user.email) {
    url.searchParams.append('requester_email', user.email);
  }

  Object.keys(params).forEach(key => {
    if (params[key] !== null) url.searchParams.append(key, params[key]);
  });

  try {
    const options = {
      method: data ? 'POST' : 'GET',
      headers: { 'Content-Type': 'application/json' }
    };
    if (data) options.body = JSON.stringify({ ...data, requester_email: user?.email });

    const response = await fetch(url.toString(), options);
    return await response.json();
  } catch (error) {
    console.error(`API Error (${action}):`, error);
    return { success: false, message: 'Connection refused' };
  }
}

export const api = {
  login: (email) => request('login', {}, { email }),
  register: (data) => request('register', {}, data),
  
  getUsers: () => request('get_users'),
  createUser: (data) => request('create_user', {}, data),
  updateUser: (data) => request('update_user', {}, { ...data, current_email: JSON.parse(localStorage.getItem('user'))?.email }),
  deleteUser: (email) => request('delete_user', {}, { email }),
  
  getSimulations: (team) => request('get_simulations', { team }),
  createSimulation: (data) => request('create_simulation', {}, data),
  updateSimulation: (data) => request('update_simulation', {}, data),
  
  getAnalytics: (team) => request('get_analytics', { team }),
  getSensorData: (simId) => request('get_sensor_data', { simulation_id: simId }),
  getUnifiedLogs: (simId, limit = 100) => request('get_unified_logs', { simulation_id: simId, limit }),
  getSystemStatus: () => request('get_status'),
};
