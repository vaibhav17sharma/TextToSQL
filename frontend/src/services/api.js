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

export const submitQuery = async (query, sessionId) => {
  try {
    const response = await api.post('/api/query', { 
      query, 
      session_id: sessionId 
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to submit query');
  }
};

export const getQueryStatus = async (queryId) => {
  try {
    const response = await api.get(`/api/query/${queryId}/status`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get query status');
  }
};

export const executeQuery = async (query, sessionId, onStatsUpdate = null) => {
  // Submit query and poll for result
  const submission = await submitQuery(query, sessionId);
  
  return new Promise((resolve, reject) => {
    let pollCount = 0;
    let pollTimeout;
    
    const poll = async () => {
      try {
        const status = await getQueryStatus(submission.query_id);
        
        // Update stats if callback provided
        if (onStatsUpdate && status.stats) {
          onStatsUpdate(status.stats);
        }
        
        if (status.status === 'completed') {
          resolve({
            result: status.result,
            stats: status.stats
          });
          return;
        } else if (status.status === 'failed') {
          reject(new Error(status.error || 'Query failed'));
          return;
        }
        
        // Schedule next poll with adaptive interval
        pollCount++;
        let nextInterval;
        if (pollCount <= 5) {
          nextInterval = 1000; // 1 sec for first 5 polls
        } else if (pollCount <= 15) {
          nextInterval = 3000; // 3 sec for next 10 polls (30 sec total)
        } else {
          nextInterval = 5000; // 5 sec after that
        }
        
        pollTimeout = setTimeout(poll, nextInterval);
        
      } catch (error) {
        reject(error);
      }
    };
    
    // Start polling
    poll();
    
    // Timeout after 5 minutes
    setTimeout(() => {
      clearTimeout(pollTimeout);
      reject(new Error('Query timeout'));
    }, 300000);
  });
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

export const getSystemStats = async () => {
  try {
    const response = await api.get('/api/system/stats');
    return response.data;
  } catch (error) {
    console.error('System stats error:', error);
    // Return mock data if API fails
    return {
      active_sessions: 0,
      total_queries: 0,
      queued: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      queue_size: 0
    };
  }
};

export const loadContext = async (sessionId) => {
  try {
    const response = await api.post('/api/context/load', {}, {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to load context');
  }
};

export const getContextStatus = async (sessionId) => {
  try {
    const response = await api.get('/api/context/status', {
      headers: { 'X-Session-ID': sessionId }
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to get context status');
  }
};