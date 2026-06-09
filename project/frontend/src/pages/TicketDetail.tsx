import React, { useEffect, useState } from 'react';
import { ArrowLeft, MessageSquare, Send, Calendar, Clock, AlertTriangle } from 'lucide-react';
import type { Ticket, User as UserType } from '../types';

interface TicketDetailProps {
  ticketId: number;
  token: string | null;
  currentUser: UserType | null;
  onBack: () => void;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const TicketDetail: React.FC<TicketDetailProps> = ({
  ticketId,
  token,
  currentUser,
  onBack,
  addToast,
}) => {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [commenting, setCommenting] = useState(false);
  const [updating, setUpdating] = useState(false);

  const fetchTicketDetails = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${ticketId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error('Failed to retrieve ticket details.');
      }
      const data = await response.json();
      setTicket(data);
    } catch (err: any) {
      addToast(err.message || 'Error loading ticket details', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token && ticketId) {
      fetchTicketDetails();
    }
  }, [token, ticketId]);

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setCommenting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${ticketId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ comment: newComment }),
      });

      if (!response.ok) {
        throw new Error('Failed to post comment.');
      }

      addToast('Comment added successfully!', 'success');
      setNewComment('');
      // Reload details to capture the comment
      await fetchTicketDetails();
    } catch (err: any) {
      addToast(err.message || 'Error posting comment', 'error');
    } finally {
      setCommenting(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    setUpdating(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${ticketId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update ticket status.');
      }

      addToast(`Status updated to ${newStatus.replace('_', ' ')}.`, 'success');
      await fetchTicketDetails();
    } catch (err: any) {
      addToast(err.message || 'Error updating status', 'error');
    } finally {
      setUpdating(false);
    }
  };

  const handlePriorityChange = async (newPriority: string) => {
    setUpdating(true);
    try {
      const response = await fetch(`http://localhost:8000/api/tickets/${ticketId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ priority: newPriority }),
      });

      if (!response.ok) {
        throw new Error('Failed to update ticket priority.');
      }

      addToast(`Priority updated to ${newPriority}.`, 'success');
      await fetchTicketDetails();
    } catch (err: any) {
      addToast(err.message || 'Error updating priority', 'error');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="p-6 text-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm max-w-lg mx-auto mt-12">
        <AlertTriangle className="w-12 h-12 text-rose-500 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 dark:text-slate-200 text-lg">Ticket Not Found</h3>
        <p className="text-slate-400 dark:text-slate-500 mt-1">This ticket may have been deleted or you do not have permission to view it.</p>
        <button onClick={onBack} className="mt-5 flex items-center gap-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold mx-auto transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Ticket Registry</span>
        </button>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      OPEN: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/50',
      IN_PROGRESS: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/50',
      RESOLVED: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/50',
      CLOSED: 'bg-slate-50 text-slate-700 border-slate-250 dark:bg-slate-900/40 dark:text-slate-400 dark:border-slate-800'
    };
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${styles[status as keyof typeof styles] || ''}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const styles = {
      LOW: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-transparent',
      MEDIUM: 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950/20 dark:text-yellow-400 dark:border-yellow-900/50',
      HIGH: 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/20 dark:text-orange-400 dark:border-orange-900/50',
      CRITICAL: 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/25 dark:text-rose-400 dark:border-rose-900/50'
    };
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${styles[priority as keyof typeof styles] || ''}`}>
        {priority}
      </span>
    );
  };

  const isAdmin = currentUser?.role === 'Admin';
  const isOwner = ticket.created_by === currentUser?.id;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back navigation header */}
      <button
        onClick={onBack}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Ticket Registry</span>
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Ticket Body Card */}
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-4">
            <div className="flex flex-wrap justify-between items-start gap-4">
              <div>
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
                  Ticket #{ticket.id}
                </span>
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">
                  {ticket.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                {getStatusBadge(ticket.status)}
                {getPriorityBadge(ticket.priority)}
              </div>
            </div>

            <hr className="border-slate-100 dark:border-slate-800" />

            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Description</h4>
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line text-sm sm:text-base">
                {ticket.description}
              </p>
            </div>

            <hr className="border-slate-100 dark:border-slate-800" />

            {/* Created Meta Info */}
            <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 dark:text-slate-500 gap-3">
              <div className="flex items-center gap-1.5">
                <div className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-bold text-indigo-500">
                  {ticket.creator.username[0].toUpperCase()}
                </div>
                <span>Submitted by <span className="font-semibold text-slate-600 dark:text-slate-400">{ticket.creator.username}</span></span>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{new Date(ticket.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Comment Thread Card */}
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-6">
            <h3 className="font-bold text-slate-800 dark:text-white text-base tracking-tight flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-indigo-500" />
              <span>Activity Timeline ({ticket.comments.length})</span>
            </h3>

            {/* Comments List */}
            {ticket.comments.length > 0 ? (
              <div className="relative pl-4 space-y-6 border-l border-slate-150 dark:border-slate-800 ml-3">
                {ticket.comments.map((comment) => (
                  <div key={comment.id} className="relative group">
                    {/* Thread node circle */}
                    <span className="absolute -left-[25px] top-1 flex items-center justify-center w-[18px] h-[18px] bg-indigo-500 dark:bg-indigo-600 rounded-full border-4 border-white dark:border-slate-900" />
                    
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                          {comment.author}
                        </span>
                        {comment.author === 'admin' && (
                          <span className="px-1.5 py-0.5 bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400 border border-indigo-150 dark:border-indigo-900/40 text-[10px] font-bold rounded">
                            Support Agent
                          </span>
                        )}
                        {comment.author === 'mcp_user' && (
                          <span className="px-1.5 py-0.5 bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400 border border-violet-150 dark:border-violet-900/40 text-[10px] font-bold rounded">
                            MCP Engine
                          </span>
                        )}
                        <span className="text-xs text-slate-400 dark:text-slate-500">
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed whitespace-pre-line">
                        {comment.comment}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-slate-400 dark:text-slate-500 text-sm">
                No activity comments recorded yet.
              </div>
            )}

            {/* Add Comment Form */}
            {(isAdmin || isOwner) && (
              <form onSubmit={handleAddComment} className="flex gap-2">
                <input
                  type="text"
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Type an update or resolution note..."
                  disabled={commenting}
                  className="flex-grow px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200"
                />
                <button
                  type="submit"
                  disabled={commenting || !newComment.trim()}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white rounded-xl text-sm font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-sm"
                >
                  {commenting ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span className="hidden sm:inline">Submit</span>
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Right Sidebar - Status Update Actions */}
        <div className="space-y-6">
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 dark:text-white text-base tracking-tight">
              Ticket Operations
            </h3>

            {/* Status Change Dropdown */}
            {(isAdmin || isOwner) && (
              <div className="space-y-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Update Status
                </label>
                <select
                  disabled={updating}
                  value={ticket.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200"
                >
                  <option value="OPEN">Open</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="RESOLVED">Resolved</option>
                  <option value="CLOSED">Closed</option>
                </select>
              </div>
            )}

            {/* Priority Change Dropdown (Admin Only) */}
            {isAdmin && (
              <div className="space-y-2 mt-4">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Override Priority
                </label>
                <select
                  disabled={updating}
                  value={ticket.priority}
                  onChange={(e) => handlePriorityChange(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200"
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
            )}

            {!isAdmin && !isOwner && (
              <div className="text-xs text-slate-400 italic">
                Only the author or administrators can alter ticket fields.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
