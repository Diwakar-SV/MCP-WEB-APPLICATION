import React, { useEffect } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';
import type { ToastMessage } from '../types';

interface ToastProps {
  toasts: ToastMessage[];
  removeToast: (id: string) => void;
}

export const Toast: React.FC<ToastProps> = ({ toasts, removeToast }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
};

const ToastItem: React.FC<{ toast: ToastMessage; onClose: () => void }> = ({ toast, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-emerald-500" />,
    error: <AlertCircle className="w-5 h-5 text-rose-500" />,
    info: <Info className="w-5 h-5 text-blue-500" />,
  };

  const bgColors = {
    success: 'bg-emerald-50 border-emerald-100 dark:bg-emerald-950/30 dark:border-emerald-900/50',
    error: 'bg-rose-50 border-rose-100 dark:bg-rose-950/30 dark:border-rose-900/50',
    info: 'bg-blue-50 border-blue-100 dark:bg-blue-950/30 dark:border-blue-900/50',
  };

  return (
    <div
      className={`pointer-events-auto flex items-center gap-3 w-80 max-w-full p-4 border rounded-xl shadow-lg backdrop-blur-md transition-all duration-300 animate-slide-in ${bgColors[toast.type]}`}
    >
      <div className="flex-shrink-0">{icons[toast.type]}</div>
      <p className="flex-grow text-sm font-medium text-slate-800 dark:text-slate-200">
        {toast.message}
      </p>
      <button
        onClick={onClose}
        className="flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg p-0.5"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
