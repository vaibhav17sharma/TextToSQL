import ChatInterface from './ChatInterface';
import QueueMonitor from './QueueMonitor';
import SchemaExplorer from './SchemaExplorer';
import SessionManager from './SessionManager';

export default function MainView() {
  return (
    <div className="flex flex-col lg:flex-row h-full gap-6 w-full">
      <div className="lg:w-1/3 min-w-0 space-y-4 overflow-y-auto">
        <div className="grid grid-cols-1 gap-4">
          <SessionManager />
          <QueueMonitor />
        </div>
        <SchemaExplorer />
      </div>
      <div className="flex-1 min-w-0">
        <ChatInterface />
      </div>
    </div>
  );
}