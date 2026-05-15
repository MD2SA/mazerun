const API_URL = 'http://127.0.0.1:8000/web/api.php';

// ─── Token storage ────────────────────────────────────────────────────────────
export const tokenStore = {
  get:    ()        => localStorage.getItem('jwt_token'),
  set:    (t)       => localStorage.setItem('jwt_token', t),
  remove: ()        => localStorage.removeItem('jwt_token'),
};

// ─── Core request function ────────────────────────────────────────────────────
async function request(action, params = {}, data = null) {
  const url = new URL(API_URL);
  url.searchParams.append('action', action);

  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined)
      url.searchParams.append(key, params[key]);
  });

  const token = tokenStore.get();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const options = {
      method: data ? 'POST' : 'GET',
      headers,
    };
    if (data) options.body = JSON.stringify(data);

    const response = await fetch(url.toString(), options);
    const result = await response.json();

    if (response.status === 401) {
      console.warn("Session expired or unauthorized");
      tokenStore.remove();
      localStorage.removeItem('user');
      // window.location.reload(); // Removed to avoid DOM issues
      return { success: false, message: 'Session expired. Please log in again.' };
    }

    return result;
  } catch (error) {
    console.error(`API Error (${action}):`, error);
    return { success: false, message: 'Connection refused' };
  }
}

// ─── API surface ──────────────────────────────────────────────────────────────
export const api = {
  // Auth (public)
  login:    (email, password)      => request('login',    {}, { email, password }),
  register: (data)                 => request('register', {}, data),

  // Users (protected)
  getUsers:   ()     => request('get_users'),
  createUser: (data) => request('create_user', {}, data),
  updateUser: (data) => request('update_user', {}, data),
  deleteUser: (email) => request('delete_user', {}, { email }),
  changePassword: (data) => request('change_password', {}, data),

  // Simulations (protected)
  getSimulations:  (team)        => request('get_simulations',  { team }),
  createSimulation:(data)        => request('create_simulation', {}, data),
  updateSimulation:(data)        => request('update_simulation', {}, data),

  // Data (protected)
  getAnalytics:   (team)         => request('get_analytics',   { team }),
  getSensorData:  (simId)        => request('get_sensor_data', { simulation_id: simId }),
  getUnifiedLogs: (simId, limit = 100) => request('get_unified_logs', { simulation_id: simId, limit }),

  // Public
  getSystemStatus: () => request('get_status'),
};
