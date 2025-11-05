import { useState, useEffect } from 'react';
import { Users, RefreshCw } from 'lucide-react';
import { getSessionStats } from '../services/api';

export default function SessionManager() {
  const [stats, setStats] = useState({ active_sessions: 0 });
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getSessionStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch session stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium flex items-center gap-2">
          <Users className="w-4 h-4" />
          Active Sessions
        </h3>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="text-gray-500 hover:text-gray-700 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>
      <div className="text-2xl font-bold text-blue-600">
        {stats.active_sessions}
      </div>
      <div className="text-xs text-gray-500">
        Connected users
      </div>
    </div>
  );
}