import React, { useState } from 'react';
import { Mail, Lock, LogIn, AlertCircle } from 'lucide-react';
import type { User } from '../types';

interface LoginProps {
  onLoginSuccess: (token: string, user: User) => void;
  addToast: (message: string, type: 'success' | 'error' | 'info') => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, addToast }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to authenticate');
      }

      addToast(`Welcome back, ${data.user.username}!`, 'success');
      onLoginSuccess(data.access_token, data.user);
    } catch (err: any) {
      setError(err.message || 'An error occurred during authentication.');
      addToast(err.message || 'Authentication failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex items-center justify-center min-h-screen p-4 overflow-hidden bg-slate-900 text-slate-100">
      {/* Decorative colored glow blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl -z-10 pointer-events-none" />

      {/* Login Card */}
      <div className="w-full max-w-md p-8 bg-slate-950/40 border border-slate-800/80 rounded-2xl shadow-2xl backdrop-blur-xl">
        {/* Header */}
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="flex items-center justify-center w-12 h-12 mb-3 bg-indigo-600 rounded-xl text-white font-bold text-xl shadow-lg shadow-indigo-600/20">
            HD
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">Welcome Back</h2>
          <p className="mt-1.5 text-sm text-slate-400">
            Sign in to access your Support Portal
          </p>
        </div>

        {/* Demo Credentials Alert Banner */}
        <div className="p-3 mb-6 border rounded-xl bg-indigo-950/20 border-indigo-900/50 text-indigo-300 text-xs leading-relaxed space-y-1">
          <p className="font-semibold text-white">Quick Access Demo Accounts:</p>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="font-semibold text-indigo-200">Admin:</span> admin@example.com / admin123
            </div>
            <div>
              <span className="font-semibold text-indigo-200">User:</span> user@example.com / user123
            </div>
          </div>
        </div>

        {/* Error notification */}
        {error && (
          <div className="flex items-center gap-2 p-3.5 mb-6 border rounded-xl bg-rose-950/20 border-rose-900/50 text-rose-300 text-sm">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email field */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-500">
                <Mail className="w-5 h-5" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-3 bg-slate-900/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 transition-all text-sm"
              />
            </div>
          </div>

          {/* Password field */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-slate-500">
                <Lock className="w-5 h-5" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-3 bg-slate-900/60 border border-slate-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none text-slate-200 transition-all text-sm"
              />
            </div>
          </div>

          {/* Login Action Button */}
          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white font-medium rounded-xl shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/25 active:scale-[0.98] transition-all text-sm duration-200"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
