import { useState, useEffect } from 'react';
import { Activity, Clock, CheckCircle, XCircle } from 'lucide-react';
import { getQueueStats } from '../services/api';

export default function QueueMonitor() {
  const [stats, setStats] = useState({
    total_queries: 0,
    queued: 0,
    processing: 0,
    completed: 0,
    failed: 0,
    queue_size: 0
  });

  const fetchStats = async () => {
    try {
      const data = await getQueueStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch queue stats:', error);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <Activity className="w-4 h-4" />
        <h3 className="text-sm font-medium">Query Queue</h3>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-yellow-500" />
          <span>Queued: {stats.queued}</span>
        </div>
        <div className="flex items-center gap-1">
          <Activity className="w-3 h-3 text-blue-500" />
          <span>Processing: {stats.processing}</span>
        </div>
        <div className="flex items-center gap-1">
          <CheckCircle className="w-3 h-3 text-green-500" />
          <span>Completed: {stats.completed}</span>
        </div>
        <div className="flex items-center gap-1">
          <XCircle className="w-3 h-3 text-red-500" />
          <span>Failed: {stats.failed}</span>
        </div>
      </div>
    </div>
  );
}