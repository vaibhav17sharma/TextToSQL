import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
console.log('API_BASE_URL:', API_BASE_URL);

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

export const getSchema = async () => {
  try {
    const response = await api.get('/api/schema');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch schema');
  }
};

export const executeQuery = async (query) => {
  try {
    const response = await api.post('/api/query', { query });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to execute query');
  }
};

export const refreshSchema = async () => {
  try {
    const response = await api.post('/api/schema/refresh');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to refresh schema');
  }
};

export const disconnectDatabase = async () => {
  try {
    const response = await api.post('/api/disconnect');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to disconnect');
  }
};