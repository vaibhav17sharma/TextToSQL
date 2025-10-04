import { useState } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import DatabaseConnection from './components/DatabaseConnection';
import MainView from './components/MainView';
import HistoryView from './components/HistoryView';
import Header from './components/Header';

function AppContent() {
  const { state } = useApp();
  const [currentView, setCurrentView] = useState('main');

  const renderContent = () => {
    if (!state.connection.isConnected) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="max-w-md w-full">
            <DatabaseConnection />
          </div>
        </div>
      );
    }

    if (currentView === 'history') {
      return <HistoryView />;
    }

    return <MainView />;
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      <Header 
        currentView={currentView} 
        onViewChange={setCurrentView} 
        isConnected={state.connection.isConnected} 
      />
      
      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-8 overflow-hidden">
        <div className="h-full w-full">
          {renderContent()}
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-600">
            Made with ❤️ and 🤖 by{' '}
            <a 
              href="https://vaibdev.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Vaibhav Sharma
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;