import React, { useEffect, useState } from 'react';
import { Search, Filter, ChevronLeft, ChevronRight, AlertCircle, Trash2, Calendar } from 'lucide-react';
import type { Ticket, User } from '../types';

interface TicketListProps {
  token: string | null;
  currentUser: User | null;
  onSelectTicket: (ticketId: number) => void;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const TicketList: React.FC<TicketListProps> = ({
  token,
  currentUser,
  onSelectTicket,
  addToast,
}) => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  // Pagination
  const [page, setPage] = useState(1);
  const limit = 10;

  const fetchTickets = async () => {
    setLoading(true);
    try {
      let url = `http://localhost:8000/api/tickets?skip=${(page - 1) * limit}&limit=${limit}`;
      if (statusFilter) url += `&status=${statusFilter}`;
      if (priorityFilter) url += `&priority=${priorityFilter}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve tickets list.');
      }
      const data = await response.json();
      setTickets(data);
    } catch (err: any) {
      addToast(err.message || 'Error fetching tickets', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchTickets();
    }
  }, [token, statusFilter, priorityFilter, page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTickets();
  };

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation(); // Avoid triggering row click selection
    if (!window.confirm(`Are you sure you want to permanently delete ticket #${id}?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete ticket');
      }

      addToast(`Ticket #${id} deleted successfully.`, 'success');
      // Reload tickets
      fetchTickets();
    } catch (err: any) {
      addToast(err.message || 'Error deleting ticket', 'error');
    }
  };

  // Status badges
  const getStatusBadge = (status: string) => {
    const styles = {
      OPEN: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/50',
      IN_PROGRESS: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/50',
      RESOLVED: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/50',
      CLOSED: 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-900/40 dark:text-slate-400 dark:border-slate-800'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status as keyof typeof styles] || ''}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  // Priority badges
  const getPriorityBadge = (priority: string) => {
    const styles = {
      LOW: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
      MEDIUM: 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950/20 dark:text-yellow-400 dark:border-yellow-900/50',
      HIGH: 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/20 dark:text-orange-400 dark:border-orange-900/50',
      CRITICAL: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/25 dark:text-rose-400 dark:border-rose-900/50 animate-pulse'
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border-transparent ${styles[priority as keyof typeof styles] || ''}`}>
        {priority}
      </span>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Filtering and Search Controls */}
      <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        <form onSubmit={handleSearchSubmit} className="flex flex-col gap-4 md:flex-row md:items-center">
          {/* Text Search Input */}
          <div className="relative flex-1">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
              <Search className="w-5 h-5" />
            </span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by ID, title, description..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-800 dark:text-slate-200 transition-all text-sm"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Status Filter */}
            <div className="flex items-center gap-1.5">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                className="px-3 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-700 dark:text-slate-300"
              >
                <option value="">All Statuses</option>
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>

            {/* Priority Filter */}
            <select
              value={priorityFilter}
              onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
              className="px-3 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-700 dark:text-slate-300"
            >
              <option value="">All Priorities</option>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>

            {/* Filter Search Button */}
            <button
              type="submit"
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold shadow-sm transition-colors"
            >
              Apply Filter
            </button>
          </div>
        </form>
      </div>

      {/* Ticket Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
          </div>
        ) : tickets.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="bg-slate-50/50 dark:bg-slate-950/30 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  <th className="px-6 py-4 w-20">ID</th>
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4 w-36">Status</th>
                  <th className="px-6 py-4 w-32">Priority</th>
                  <th className="px-6 py-4 w-44">Created Date</th>
                  {currentUser?.role === 'Admin' && <th className="px-6 py-4 w-20 text-center">Actions</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-150 dark:divide-slate-800 text-sm">
                {tickets.map((ticket) => (
                  <tr
                    key={ticket.id}
                    onClick={() => onSelectTicket(ticket.id)}
                    className="hover:bg-slate-50/70 dark:hover:bg-slate-800/30 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 font-bold text-indigo-600 dark:text-indigo-400">
                      #{ticket.id}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-800 dark:text-slate-100 max-w-xs sm:max-w-md truncate">
                      <div className="font-semibold">{ticket.title}</div>
                      <div className="text-xs text-slate-400 dark:text-slate-500 font-normal mt-0.5 truncate">
                        {ticket.description}
                      </div>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(ticket.status)}</td>
                    <td className="px-6 py-4">{getPriorityBadge(ticket.priority)}</td>
                    <td className="px-6 py-4 text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-2.5 md:mt-0">
                      <Calendar className="w-4 h-4 text-slate-400" />
                      <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                    </td>
                    {currentUser?.role === 'Admin' && (
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={(e) => handleDelete(e, ticket.id)}
                          className="p-2 text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-xl transition-all"
                          title="Delete ticket"
                        >
                          <Trash2 className="w-4.5 h-4.5" />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <AlertCircle className="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
            <h3 className="font-semibold text-slate-700 dark:text-slate-300 text-lg">No tickets found</h3>
            <p className="text-slate-400 dark:text-slate-500 text-sm max-w-sm mt-1">
              Try adjusting your query or filters to find what you are looking for.
            </p>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-400 dark:text-slate-500">
            Showing Page <span className="font-bold text-slate-700 dark:text-slate-300">{page}</span>
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center justify-center p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 rounded-xl"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={tickets.length < limit}
              className="flex items-center justify-center p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 rounded-xl"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
