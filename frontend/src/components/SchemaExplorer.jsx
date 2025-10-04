import { useState } from 'react';
import { Table, ChevronDown, ChevronRight, Key, Link, RefreshCw, Unplug } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { refreshSchema, disconnectDatabase } from '../services/api';

export default function SchemaExplorer() {
  const { state, dispatch } = useApp();
  const [expandedTables, setExpandedTables] = useState(new Set());

  const toggleTable = (tableName) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const handleRefreshSchema = async () => {
    dispatch({ type: 'SET_SCHEMA_LOADING', payload: true });
    try {
      const schema = await refreshSchema();
      dispatch({ type: 'SET_SCHEMA_SUCCESS', payload: schema.tables });
    } catch (error) {
      dispatch({ type: 'SET_SCHEMA_ERROR', payload: error.message });
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectDatabase();
      dispatch({ type: 'DISCONNECT_DATABASE' });
    } catch (error) {
      dispatch({ type: 'SET_CONNECTION_ERROR', payload: error.message });
    }
  };

  if (!state.connection.isConnected) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <Table className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600">Connect to a database to explore schema</p>
      </div>
    );
  }

  if (state.schema.loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Table className="w-5 h-5" />
          Database Schema
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefreshSchema}
            disabled={state.schema.loading}
            className="flex items-center gap-2 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${state.schema.loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleDisconnect}
            className="flex items-center gap-2 px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
          >
            <Unplug className="w-4 h-4" />
            Disconnect
          </button>
        </div>
      </div>

      {state.schema.error ? (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {state.schema.error}
        </div>
      ) : (
        <div className="space-y-2 flex-1 overflow-y-auto">
          {state.schema.tables.map((table) => (
            <div key={table.name} className="border border-gray-200 rounded-lg">
              <button
                onClick={() => toggleTable(table.name)}
                className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-2">
                  <Table className="w-4 h-4 text-blue-600" />
                  <span className="font-medium">{table.name}</span>
                  <span className="text-sm text-gray-500">
                    ({table.columns.length} columns)
                  </span>
                </div>
                {expandedTables.has(table.name) ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>
              
              {expandedTables.has(table.name) && (
                <div className="px-4 pb-3">
                  <div className="space-y-2">
                    {table.columns.map((column) => (
                      <div
                        key={column.name}
                        className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm">{column.name}</span>
                          {column.primary_key && (
                            <Key className="w-3 h-3 text-yellow-600" title="Primary Key" />
                          )}
                          {column.foreign_key && (
                            <Link className="w-3 h-3 text-blue-600" title={`Foreign Key: ${column.foreign_key}`} />
                          )}
                        </div>
                        <span className="text-xs text-gray-600 font-mono">
                          {column.type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}