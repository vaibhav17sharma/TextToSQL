import SchemaExplorer from './SchemaExplorer';
import ChatInterface from './ChatInterface';

export default function MainView() {
  return (
    <div className="flex flex-col lg:flex-row h-full gap-6 w-full">
      <div className="lg:w-1/3 min-w-0">
        <SchemaExplorer />
      </div>
      <div className="flex-1 min-w-0">
        <ChatInterface />
      </div>
    </div>
  );
}