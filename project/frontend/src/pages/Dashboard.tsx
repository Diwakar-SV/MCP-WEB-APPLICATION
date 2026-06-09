import React, { useEffect, useState } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';
import { Inbox, CheckCircle2, AlertTriangle, Activity, RefreshCw } from 'lucide-react';
import type { DashboardStats } from '../types';

interface DashboardProps {
  token: string | null;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ token, addToast }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/stats', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to load dashboard metrics');
      }
      const data = await response.ok ? await response.json() : null;
      if (data) {
        setStats(data);
      }
    } catch (err: any) {
      addToast(err.message || 'Error loading dashboard metrics', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchStats();
    }
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
          <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Aggregating real-time stats...</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center p-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        <p className="text-slate-500 dark:text-slate-400">Failed to load statistics.</p>
        <button onClick={fetchStats} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium">
          Retry
        </button>
      </div>
    );
  }

  // Formatting for Recharts
  const pieColors = {
    'OPEN': '#f59e0b',       // Amber
    'IN_PROGRESS': '#3b82f6',// Blue
    'RESOLVED': '#10b981',   // Emerald
    'CLOSED': '#64748b'      // Slate
  };

  const pieData = stats.status_distribution.map(item => ({
    name: item.status.replace('_', ' '),
    value: item.count,
    color: pieColors[item.status as keyof typeof pieColors] || '#a855f7'
  })).filter(item => item.value > 0);

  const statsCards = [
    {
      title: 'Total Tickets',
      value: stats.total_tickets,
      icon: <Inbox className="w-6 h-6 text-indigo-500" />,
      bg: 'bg-indigo-50/50 dark:bg-indigo-950/20 border-indigo-100/50 dark:border-indigo-900/30',
      label: 'All registered requests'
    },
    {
      title: 'Open Tickets',
      value: stats.open_tickets,
      icon: <Activity className="w-6 h-6 text-amber-500" />,
      bg: 'bg-amber-50/50 dark:bg-amber-950/20 border-amber-100/50 dark:border-amber-900/30',
      label: 'Awaiting support action'
    },
    {
      title: 'Resolved Tickets',
      value: stats.resolved_tickets,
      icon: <CheckCircle2 className="w-6 h-6 text-emerald-500" />,
      bg: 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-100/50 dark:border-emerald-900/30',
      label: 'Completed and closed'
    },
    {
      title: 'High Priority',
      value: stats.high_priority_tickets,
      icon: <AlertTriangle className="w-6 h-6 text-rose-500" />,
      bg: 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-100/50 dark:border-rose-900/30',
      label: 'Critical / High issues'
    }
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Action / Refresh */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">Overview of operational tickets status</h3>
        </div>
        <button
          onClick={fetchStats}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh metrics</span>
        </button>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card, idx) => (
          <div
            key={idx}
            className={`p-6 border rounded-2xl shadow-sm ${card.bg} transition-all duration-300 hover:shadow-md`}
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-semibold tracking-wide text-slate-500 dark:text-slate-400 uppercase">
                  {card.title}
                </p>
                <h4 className="mt-2 text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  {card.value}
                </h4>
              </div>
              <div className="p-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-800 shadow-sm">
                {card.icon}
              </div>
            </div>
            <p className="mt-3 text-xs font-medium text-slate-400 dark:text-slate-500">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Visual Analytics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Tickets Per Day Chart */}
        <div className="lg:col-span-2 p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
          <h3 className="font-bold text-slate-800 dark:text-white text-base tracking-tight mb-6">
            Daily Ticket Trends
          </h3>
          <div className="h-80 w-full">
            {stats.tickets_per_day && stats.tickets_per_day.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.tickets_per_day}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" className="dark:stroke-slate-800" />
                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    dy={10}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    dx={-10}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderRadius: '12px',
                      border: 'none',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#4f46e5"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorCount)"
                    name="Submitted Tickets"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400">
                No telemetry available for ticket counts.
              </div>
            )}
          </div>
        </div>

        {/* Status Distribution Chart */}
        <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col">
          <h3 className="font-bold text-slate-800 dark:text-white text-base tracking-tight mb-6">
            Status Share
          </h3>
          <div className="flex-1 min-h-[260px] flex items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="45%"
                    innerRadius={65}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      borderRadius: '12px',
                      border: 'none',
                      color: '#fff',
                      fontSize: '12px',
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    iconSize={8}
                    formatter={(value) => <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-slate-400 text-sm flex flex-col items-center gap-1">
                <span>No tickets on record.</span>
                <span className="text-xs text-slate-500">Distribution will populate when tickets are created.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
