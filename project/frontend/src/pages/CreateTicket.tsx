import React, { useState } from 'react';
import { ArrowRight, FileText } from 'lucide-react';

interface CreateTicketProps {
  token: string | null;
  onSuccess: () => void;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const CreateTicket: React.FC<CreateTicketProps> = ({ token, onSuccess, addToast }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('LOW');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      addToast('Please fill in both title and description.', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title,
          description,
          priority
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit ticket request.');
      }

      addToast('Ticket created successfully!', 'success');
      setTitle('');
      setDescription('');
      setPriority('LOW');
      onSuccess(); // Navigate back to the list
    } catch (err: any) {
      addToast(err.message || 'Error creating ticket', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Header */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-xl">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 dark:text-white text-lg tracking-tight">Create Support Ticket</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500">Submit details below and a support agent will reach out</p>
            </div>
          </div>

          <hr className="border-slate-100 dark:border-slate-800" />

          {/* Ticket Title */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Ticket Title
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Docker daemon failing to startup"
              className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>

          {/* Issue Priority */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Issue Priority
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((p) => {
                const isActive = priority === p;
                const borderColors = {
                  LOW: 'border-slate-200 hover:border-slate-400 text-slate-700 bg-slate-50 dark:bg-slate-950 dark:border-slate-800',
                  MEDIUM: 'border-yellow-200 hover:border-yellow-400 text-yellow-700 bg-yellow-50/20 dark:bg-yellow-950/10 dark:border-yellow-900/40',
                  HIGH: 'border-orange-200 hover:border-orange-400 text-orange-700 bg-orange-50/20 dark:bg-orange-950/10 dark:border-orange-900/40',
                  CRITICAL: 'border-rose-200 hover:border-rose-400 text-rose-700 bg-rose-50/20 dark:bg-rose-950/10 dark:border-rose-900/40'
                };
                const activeColors = {
                  LOW: 'bg-slate-100 border-slate-600 dark:bg-slate-800 dark:border-slate-500 dark:text-white',
                  MEDIUM: 'bg-yellow-100 border-yellow-500 dark:bg-yellow-900/35 dark:border-yellow-500 text-yellow-800 dark:text-yellow-300',
                  HIGH: 'bg-orange-100 border-orange-500 dark:bg-orange-900/35 dark:border-orange-500 text-orange-800 dark:text-orange-300',
                  CRITICAL: 'bg-rose-100 border-rose-500 dark:bg-rose-900/35 dark:border-rose-500 text-rose-800 dark:text-rose-300'
                };

                return (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPriority(p)}
                    className={`px-3 py-2.5 text-center text-xs font-bold border rounded-xl transition-all ${
                      isActive ? activeColors[p as keyof typeof activeColors] : borderColors[p as keyof typeof borderColors]
                    }`}
                  >
                    {p}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Ticket Description */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Detailed Description
            </label>
            <textarea
              required
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide context, reproduction steps, log outputs, or error codes..."
              className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-sm outline-none focus:border-indigo-500 text-slate-800 dark:text-slate-200 focus:ring-1 focus:ring-indigo-500 transition-all resize-y"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-1.5 w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 hover:shadow-lg transition-all active:scale-[0.98] duration-200 text-sm"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>Submit Ticket</span>
                <ArrowRight className="w-4.5 h-4.5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
