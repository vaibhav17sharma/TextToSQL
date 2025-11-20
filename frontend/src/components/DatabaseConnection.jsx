import { useState } from 'react';
import { Database, Upload, Loader2, Download } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { connectDatabase, connectDatabaseFile, getSchema, downloadSampleDatabase } from '../services/api';

export default function DatabaseConnection() {
  const { state, dispatch } = useApp();
  const [connectionType, setConnectionType] = useState('credentials');
  const [formData, setFormData] = useState({
    host: '',
    port: '',
    username: '',
    password: '',
    database: '',
    db_type: 'postgresql'
  });

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleConnect = async (e) => {
    e.preventDefault();
    dispatch({ type: 'SET_CONNECTION_LOADING', payload: true });
    
    try {
      const connectionData = {
        type: 'credentials',
        ...formData,
        port: parseInt(formData.port)
      };
      
      const result = await connectDatabase(connectionData);
      dispatch({ type: 'SET_CONNECTION_SUCCESS', payload: result });
      
      // Fetch schema after successful connection
      dispatch({ type: 'SET_SCHEMA_LOADING', payload: true });
      const schema = await getSchema(result.session_id);
      dispatch({ type: 'SET_SCHEMA_SUCCESS', payload: schema.tables });
    } catch (error) {
      dispatch({ type: 'SET_CONNECTION_ERROR', payload: error.message });
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    dispatch({ type: 'SET_CONNECTION_LOADING', payload: true });
    
    try {
      const result = await connectDatabaseFile(file);
      dispatch({ type: 'SET_CONNECTION_SUCCESS', payload: result });
      
      dispatch({ type: 'SET_SCHEMA_LOADING', payload: true });
      const schema = await getSchema(result.session_id);
      dispatch({ type: 'SET_SCHEMA_SUCCESS', payload: schema.tables });
    } catch (error) {
      dispatch({ type: 'SET_CONNECTION_ERROR', payload: error.message });
    }
  };

  const handleLoadSampleDatabase = async () => {
    dispatch({ type: 'SET_CONNECTION_LOADING', payload: true });
    
    try {
      const blob = await downloadSampleDatabase();
      const file = new File([blob], 'sample_ecommerce.db', { type: 'application/octet-stream' });
      
      const result = await connectDatabaseFile(file);
      dispatch({ type: 'SET_CONNECTION_SUCCESS', payload: result });
      
      dispatch({ type: 'SET_SCHEMA_LOADING', payload: true });
      const schema = await getSchema(result.session_id);
      dispatch({ type: 'SET_SCHEMA_SUCCESS', payload: schema.tables });
    } catch (error) {
      dispatch({ type: 'SET_CONNECTION_ERROR', payload: error.message });
    }
  };

  if (state.connection.isConnected) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-green-700">
          <Database className="w-5 h-5" />
          <span className="font-medium">Connected to database</span>
          {state.session.connectionId && (
            <span className="text-xs bg-green-100 px-2 py-1 rounded">
              {state.session.connectionId}
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Database className="w-5 h-5" />
        {connectionType === 'credentials' ? 'Enter your PostgreSQL details' : 'Upload your SQLite file'}
      </h2>

      <div className="mb-4">
        <div className="flex gap-2">
          <button
            onClick={() => setConnectionType('credentials')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              connectionType === 'credentials'
                ? 'bg-blue-100 text-blue-700 border border-blue-300'
                : 'bg-gray-100 text-gray-700 border border-gray-300'
            }`}
          >
            Database Credentials
          </button>
          <button
            onClick={() => setConnectionType('file')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              connectionType === 'file'
                ? 'bg-blue-100 text-blue-700 border border-blue-300'
                : 'bg-gray-100 text-gray-700 border border-gray-300'
            }`}
          >
            Upload File
          </button>
        </div>
      </div>

      {connectionType === 'credentials' ? (
        <form onSubmit={handleConnect} className="space-y-4">

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Host</label>
              <input
                type="text"
                name="host"
                value={formData.host}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="localhost"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Port</label>
              <input
                type="text"
                name="port"
                value={formData.port}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="5432"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Database Name</label>
            <input
              type="text"
              name="database"
              value={formData.database}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="mydb"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="username"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="password"
                required
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={state.connection.loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {state.connection.loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Connecting...
              </>
            ) : (
              'Connect'
            )}
          </button>
        </form>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Database File (.db, .sqlite, .sql)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".db,.sqlite,.sql"
              className="hidden"
              id="file-upload"
              disabled={state.connection.loading}
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700"
            >
              {state.connection.loading ? 'Uploading...' : 'Click to upload or drag and drop'}
            </label>
          </div>
        </div>
      )}

      {state.connection.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {state.connection.error}
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-3">Or try with sample data</p>
          <button
            onClick={handleLoadSampleDatabase}
            disabled={state.connection.loading}
            className="px-6 py-2 rounded-md text-sm font-medium bg-green-100 text-green-700 border border-green-300 hover:bg-green-200 disabled:opacity-50 flex items-center gap-2 mx-auto"
          >
            <Download className="w-4 h-4" />
            Load Sample Database
          </button>
        </div>
      </div>
    </div>
  );
}