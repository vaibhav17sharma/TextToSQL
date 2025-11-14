import { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import QueueMonitor from './QueueMonitor';
import SchemaExplorer from './SchemaExplorer';
import SessionManager from './SessionManager';
import SystemStatus from './SystemStatus';
import ContextLoader from './ContextLoader';
import { useApp } from '../context/AppContext';
import { getSystemStats, getContextStatus } from '../services/api';

export default function MainView() {
  const { state } = useApp();
  const [stats, setStats] = useState(null);
  const [contextLoaded, setContextLoaded] = useState(false);

  const handleStatsUpdate = (newStats) => {
    setStats(newStats);
  };

  // Initial stats load and periodic refresh
  useEffect(() => {
    const loadInitialStats = async () => {
      try {
        const initialStats = await getSystemStats();
        setStats(initialStats);
      } catch (error) {
        console.error('Failed to load initial stats:', error);
      }
    };
    
    loadInitialStats();
    
    // Refresh stats every 30 seconds as fallback
    const interval = setInterval(async () => {
      try {
        const refreshedStats = await getSystemStats();
        setStats(refreshedStats);
      } catch (error) {
        console.error('Failed to refresh stats:', error);
      }
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Check context status when connection changes
  useEffect(() => {
    const checkInitialContext = async () => {
      if (state.connection.isConnected && state.session.sessionId) {
        try {
          const status = await getContextStatus(state.session.sessionId);
          setContextLoaded(status.loaded);
        } catch (error) {
          setContextLoaded(false);
        }
      } else {
        setContextLoaded(false);
      }
    };
    
    checkInitialContext();
  }, [state.connection.isConnected, state.session.sessionId]);

  return (
    <div className="flex flex-col lg:flex-row h-full gap-6 w-full">
      <div className="lg:w-1/3 min-w-0 space-y-4 overflow-y-auto">
        <SystemStatus stats={stats} />
        <div className="grid grid-cols-1 gap-4">
          <SessionManager stats={stats} />
          <QueueMonitor stats={stats} />
        </div>
        <ContextLoader contextLoaded={contextLoaded} setContextLoaded={setContextLoaded} />
        <SchemaExplorer />
      </div>
      <div className="flex-1 min-w-0">
        <ChatInterface onStatsUpdate={handleStatsUpdate} contextLoaded={contextLoaded} setContextLoaded={setContextLoaded} />
      </div>
    </div>
  );
}