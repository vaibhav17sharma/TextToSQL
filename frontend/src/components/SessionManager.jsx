import { Users } from 'lucide-react';

export default function SessionManager({ stats = null, onRefresh = null }) {
  const defaultStats = { active_sessions: 0 };
  const currentStats = stats || defaultStats;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium flex items-center gap-2">
          <Users className="w-4 h-4" />
          Active Sessions
        </h3>
      </div>
      <div className="text-2xl font-bold text-blue-600">
        {currentStats.active_sessions}
      </div>
      <div className="text-xs text-gray-500">
        Connected users
      </div>
    </div>
  );
}