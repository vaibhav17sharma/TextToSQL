import axios from 'axios';

// Use relative URL since Vite proxy will handle routing to backend
const API_BASE_URL = '';
console.log('Using Vite proxy for API requests');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock data for development
const mockSchema = {
  tables: [
    {
      name: 'users',
      columns: [
        { name: 'id', type: 'INTEGER', primary_key: true },
        { name: 'name', type: 'VARCHAR(100)' },
        { name: 'email', type: 'VARCHAR(255)' },
        { name: 'created_at', type: 'TIMESTAMP' }
      ]
    },
    {
      name: 'orders',
      columns: [
        { name: 'id', type: 'INTEGER', primary_key: true },
        { name: 'user_id', type: 'INTEGER', foreign_key: 'users.id' },
        { name: 'total', type: 'DECIMAL(10,2)' },
        { name: 'status', type: 'VARCHAR(50)' }
      ]
    }
  ]
};

const mockQueryResult = {
  sql: 'SELECT name, email FROM users WHERE created_at > \'2023-01-01\'',
  results: [
    { name: 'John Doe', email: 'john@example.com' },
    { name: 'Jane Smith', email: 'jane@example.com' }
  ],
  execution_time: 0.045
};

export const connectDatabase = async (config) => {
  try {
    const response = await api.post('/api/connect-db', config);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to connect to database');
  }
};

export const connectDatabaseFile = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/connect-db/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to connect to database file');
  }
};

export const getSchema = async (sessionId) => {
  try {
    const response = await api.get('/api/schema', {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch schema');
  }
};

export const executeQuery = async (query, sessionId) => {
  try {
    const response = await api.post('/api/query', { 
      query, 
      session_id: sessionId 
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to execute query');
  }
};

export const refreshSchema = async (sessionId) => {
  try {
    const response = await api.post('/api/schema/refresh', {}, {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to refresh schema');
  }
};

export const disconnectDatabase = async (sessionId) => {
  try {
    const response = await api.post('/api/disconnect', {}, {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to disconnect');
  }
};

export const getConnectionStatus = async (sessionId) => {
  try {
    const response = await api.get('/api/connection/status', {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get connection status');
  }
};

export const getSessionStats = async () => {
  try {
    const response = await api.get('/api/sessions/stats');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get session stats');
  }
};