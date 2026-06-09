import React from 'react';
import { Menu, Sun, Moon, Sparkles } from 'lucide-react';
import type { User } from '../types';

interface TopbarProps {
  currentPage: string;
  user: User | null;
  darkMode: boolean;
  setDarkMode: (dark: boolean) => void;
  toggleSidebar: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentPage,
  user,
  darkMode,
  setDarkMode,
  toggleSidebar,
}) => {
  const getPageTitle = () => {
    switch (currentPage) {
      case 'dashboard':
        return 'System Dashboard';
      case 'tickets':
        return 'Ticket Registry';
      case 'create-ticket':
        return 'File New Support Ticket';
      case 'ticket-detail':
        return 'Support Ticket Detail';
      case 'kb':
        return 'Knowledge Base Search';
      default:
        return 'Help Desk Support';
    }
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 backdrop-blur-md">
      {/* Left side: Hamburger + Page Title */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="font-semibold text-slate-800 dark:text-slate-100 text-lg sm:text-xl tracking-tight">
            {getPageTitle()}
          </h2>
        </div>
      </div>

      {/* Right side: Dark Mode Toggle + User avatar indicator */}
      <div className="flex items-center gap-3">
        {/* Sparkle badge for Premium aesthetic */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 text-xs font-semibold rounded-full border border-indigo-100 dark:border-indigo-900/50">
          <Sparkles className="w-3.5 h-3.5" />
          <span>MCP Powered</span>
        </div>

        {/* Dark Mode toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2.5 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
          title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {darkMode ? <Sun className="w-5 h-5 text-amber-500" /> : <Moon className="w-5 h-5 text-indigo-500" />}
        </button>

        {/* User profile identifier */}
        {user && (
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
            <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-semibold flex items-center justify-center text-sm">
              {user.username[0].toUpperCase()}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
