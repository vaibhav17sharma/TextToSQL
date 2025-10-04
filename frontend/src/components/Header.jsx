import { History, Trash2 } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function Header({ currentView, onViewChange, isConnected }) {
  const { dispatch } = useApp();

  const handleClearChat = () => {
    dispatch({ type: 'CLEAR_CHAT' });
  };
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center py-4 gap-2">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
            Text-to-SQL AI Assistant
          </h1>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-4">
            {isConnected && (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onViewChange(currentView === 'history' ? 'main' : 'history')}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors"
                >
                  <History className="w-4 h-4" />
                  <span className="hidden sm:inline">{currentView === 'history' ? 'Back to Query' : 'Session History'}</span>
                  <span className="sm:hidden">{currentView === 'history' ? 'Back' : 'History'}</span>
                </button>
                <button
                  onClick={handleClearChat}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600 transition-colors"
                  title="Clear chat"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Clear</span>
                </button>
              </div>
            )}
            <div className="text-xs sm:text-sm text-gray-500">
              Convert natural language to SQL queries
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}