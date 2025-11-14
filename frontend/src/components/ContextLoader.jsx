import { useState, useEffect } from 'react';
import { Database, Loader2, CheckCircle, AlertCircle, Play } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { loadContext, getContextStatus } from '../services/api';

export default function ContextLoader() {
  const { state } = useApp();
  const [loading, setLoading] = useState(false);
  const [contextStatus, setContextStatus] = useState({ loaded: false, message: '' });
  const [loadResult, setLoadResult] = useState(null);

  useEffect(() => {
    if (state.connection.isConnected && state.session.sessionId) {
      checkContextStatus();
    }
  }, [state.connection.isConnected, state.session.sessionId]);

  const checkContextStatus = async () => {
    try {
      const status = await getContextStatus(state.session.sessionId);
      setContextStatus(status);
    } catch (error) {
      console.error('Failed to check context status:', error);
    }
  };

  const handleLoadContext = async () => {
    if (!state.session.sessionId) return;
    
    setLoading(true);
    setLoadResult(null);
    
    try {
      const result = await loadContext(state.session.sessionId);
      setLoadResult(result);
      setContextStatus({ loaded: true, message: 'Context loaded successfully' });
    } catch (error) {
      setLoadResult({ success: false, message: error.message });
    } finally {
      setLoading(false);
    }
  };

  const formatSampleResults = (sampleResults) => {
    if (!sampleResults || sampleResults.length === 0) return null;

    return (
      <div className="mt-4 space-y-3">
        <h4 className="text-sm font-medium text-gray-700">Sample Data Preview:</h4>
        {sampleResults.map((sample, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-800">{sample.table}</span>
              {sample.execution_time && (
                <span className="text-xs text-gray-500">{sample.execution_time}s</span>
              )}
            </div>
            
            {sample.error ? (
              <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
                Error: {sample.error}
              </div>
            ) : (
              <div>
                <code className="text-xs bg-gray-800 text-green-400 p-2 rounded block mb-2">
                  {sample.sql}
                </code>
                {sample.results && sample.results.length > 0 && (
                  <div className="text-xs text-gray-600">
                    Found {sample.results.length} row(s) with {Object.keys(sample.results[0]).length} column(s)
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  if (!state.connection.isConnected) {
    return null;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Database className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold">Context Loader</h3>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2">
          {contextStatus.loaded ? (
            <CheckCircle className="w-4 h-4 text-green-600" />
          ) : (
            <AlertCircle className="w-4 h-4 text-orange-500" />
          )}
          <span className="text-sm text-gray-700">{contextStatus.message}</span>
        </div>

        {!contextStatus.loaded && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800 mb-3">
              Load database schema to the AI model for better query generation. This will also run a sample query on the first table to preview your data.
            </p>
            <button
              onClick={handleLoadContext}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 text-sm"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {loading ? 'Loading Context...' : 'Load Context'}
            </button>
          </div>
        )}

        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span className="text-sm text-blue-800">Loading schema context to AI model...</span>
            </div>
            <div className="text-xs text-blue-600">This may take a few moments...</div>
          </div>
        )}

        {loadResult && (
          <div className={`rounded-lg p-3 ${
            loadResult.success 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {loadResult.success ? (
                <CheckCircle className="w-4 h-4 text-green-600" />
              ) : (
                <AlertCircle className="w-4 h-4 text-red-600" />
              )}
              <span className={`text-sm font-medium ${
                loadResult.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {loadResult.message}
              </span>
            </div>
            
            {loadResult.success && loadResult.tables_count && (
              <div className="text-sm text-green-700 mb-2">
                Loaded {loadResult.tables_count} table(s) to AI context
              </div>
            )}
            
            {loadResult.sample_results && formatSampleResults(loadResult.sample_results)}
          </div>
        )}

        {contextStatus.loaded && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">Ready for Queries</span>
            </div>
            <p className="text-sm text-green-700">
              Database context is loaded. You can now ask natural language questions about your data.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}