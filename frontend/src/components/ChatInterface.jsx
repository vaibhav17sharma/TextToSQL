import { AlertCircle, Clock, Loader2, MessageSquare, Send, Database } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useApp } from '../context/AppContext';
import { executeQuery, getContextStatus } from '../services/api';

export default function ChatInterface({ onStatsUpdate = null }) {
  const { state, dispatch } = useApp();
  const [input, setInput] = useState('');
  const [contextLoaded, setContextLoaded] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.chat.messages]);

  useEffect(() => {
    if (state.connection.isConnected && state.session.sessionId) {
      checkContextStatus();
    }
  }, [state.connection.isConnected, state.session.sessionId]);

  const checkContextStatus = async () => {
    try {
      const status = await getContextStatus(state.session.sessionId);
      setContextLoaded(status.loaded);
    } catch (error) {
      console.error('Failed to check context status:', error);
      setContextLoaded(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !state.connection.isConnected) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_CHAT_LOADING', payload: true });
    dispatch({ type: 'ADD_TO_HISTORY', payload: { query: input, timestamp: new Date() } });

    setInput('');

    try {
      const { result, stats } = await executeQuery(
        input, 
        state.session.sessionId,
        onStatsUpdate
      );
      
      // Update stats if available
      if (stats && onStatsUpdate) {
        onStatsUpdate(stats);
      }
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result,
        timestamp: new Date()
      };

      dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      dispatch({ type: 'SET_CHAT_LOADING', payload: false });
    } catch (error) {
      dispatch({ type: 'SET_CHAT_ERROR', payload: error.message });
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: error.message,
        timestamp: new Date()
      };
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage });
    }
  };

  const formatResults = (results) => {
    if (!results || results.length === 0) return null;

    const columns = Object.keys(results[0]);
    
    return (
      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-4 py-2 text-left text-sm font-medium text-gray-700 border-b">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                {columns.map((column) => (
                  <td key={column} className="px-4 py-2 text-sm text-gray-900 border-b">
                    {row[column]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  if (!state.connection.isConnected) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <MessageSquare className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600">Connect to a database to start querying</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Query Assistant
          <span className='ml-auto'>
            {state.session.sessionId && (
            <span className="text-xs bg-blue-100 px-2 py-1 rounded text-blue-700">
              Session: {state.session.sessionId.slice(0, 8)}
            </span>
          )}
          </span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {state.chat.messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            {contextLoaded ? (
              <div>
                <p>Ask me anything about your data!</p>
                <p className="text-sm mt-2">Try: "Show me all users" or "What are the top selling products?"</p>
              </div>
            ) : (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mx-4">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="w-5 h-5 text-orange-600" />
                  <span className="font-medium text-orange-800">Context Not Loaded</span>
                </div>
                <p className="text-sm text-orange-700">
                  Please load the database context first using the Context Loader above for better query generation.
                </p>
              </div>
            )}
          </div>
        ) : (
          state.chat.messages.map((message) => (
            <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-3/4 rounded-lg p-3 ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : message.type === 'error'
                  ? 'bg-red-50 border border-red-200 text-red-700'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                {message.type === 'user' ? (
                  <p>{message.content}</p>
                ) : message.type === 'error' ? (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    <p>{message.content}</p>
                  </div>
                ) : (
                  <div>
                    <div className="mb-2">
                      <p className="text-sm text-gray-600 mb-1">Generated SQL:</p>
                      <code className="bg-gray-800 text-green-400 p-2 rounded text-sm block">
                        {message.content.sql}
                      </code>
                    </div>
                    {message.content.results && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Results:</p>
                        {formatResults(message.content.results)}
                        <p className="text-xs text-gray-500 mt-2">
                          Executed in {message.content.execution_time}s
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {state.chat.loading && (
          <div className="flex justify-start">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center gap-2">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-blue-700">Queued</span>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span className="text-blue-700">Processing query...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your data..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={state.chat.loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || state.chat.loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            title={!contextLoaded ? 'Consider loading context first for better results' : ''}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}