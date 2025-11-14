import { Activity, CheckCircle, AlertCircle, Users } from 'lucide-react';

export default function SystemOverview({ stats = null }) {
  const defaultStats = {
    active_sessions: 0,
    total_queries: 0,
    queued: 0,
    processing: 0,
    completed: 0,
    failed: 0,
    queue_size: 0
  };
  
  const currentStats = stats || defaultStats;
  const isHealthy = currentStats.processing < 5 && currentStats.queued < 10;
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium">System Overview</span>
        </div>
        <div className="flex items-center gap-1">
          {isHealthy ? (
            <CheckCircle className="w-4 h-4 text-green-500" />
          ) : (
            <AlertCircle className="w-4 h-4 text-yellow-500" />
          )}
          <span className={`text-xs font-medium ${
            isHealthy ? 'text-green-600' : 'text-yellow-600'
          }`}>
            {isHealthy ? 'Healthy' : 'Busy'}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Users className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-gray-600">Active Sessions</span>
          </div>
          <div className="text-xl font-bold text-blue-600">
            {currentStats.active_sessions}
          </div>
        </div>
        
        <div>
          <div className="text-xs text-gray-600 mb-1">Queue Status</div>
          <div className="text-xs text-gray-500">
            {currentStats.processing > 0 && (
              <span>Processing {currentStats.processing}</span>
            )}
            {currentStats.queued > 0 && (
              <span className={currentStats.processing > 0 ? 'ml-2' : ''}>
                {currentStats.queued} queued
              </span>
            )}
            {currentStats.processing === 0 && currentStats.queued === 0 && (
              <span>Ready for queries</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}