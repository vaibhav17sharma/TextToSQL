import { Clock, RotateCcw } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function SessionHistory() {
  const { state, dispatch } = useApp();

  const handleRerunQuery = (query) => {
    // Add the query back to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };
    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 h-full flex flex-col">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Clock className="w-5 h-5" />
        Session History
      </h2>

      {state.history.length === 0 ? (
        <div className="text-center text-gray-500 py-4">
          <p>No queries yet</p>
          <p className="text-sm mt-1">Your query history will appear here</p>
        </div>
      ) : (
        <div className="space-y-2 flex-1 overflow-y-auto">
          {state.history.map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {item.query}
                </p>
                <p className="text-xs text-gray-500">
                  {formatTime(item.timestamp)}
                </p>
              </div>
              <button
                onClick={() => handleRerunQuery(item.query)}
                className="ml-2 p-1 text-gray-400 hover:text-blue-600 transition-colors"
                title="Rerun query"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {state.history.length > 0 && (
        <button
          onClick={() => dispatch({ type: 'CLEAR_CHAT' })}
          className="mt-4 w-full text-sm text-gray-600 hover:text-gray-800 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          Clear Chat
        </button>
      )}
    </div>
  );
}