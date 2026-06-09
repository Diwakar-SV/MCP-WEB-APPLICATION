import React from 'react';
import { LayoutDashboard, Ticket, PlusCircle, BookOpen, LogOut, Shield } from 'lucide-react';
import type { User } from '../types';

interface SidebarProps {
  currentPage: string;
  setCurrentPage: (page: string) => void;
  user: User | null;
  onLogout: () => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  setCurrentPage,
  user,
  onLogout,
  isOpen,
  setIsOpen,
}) => {
  const menuItems = [
    { id: 'dashboard', name: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'tickets', name: 'Tickets', icon: <Ticket className="w-5 h-5" /> },
    { id: 'create-ticket', name: 'Create Ticket', icon: <PlusCircle className="w-5 h-5" /> },
    { id: 'kb', name: 'Knowledge Base', icon: <BookOpen className="w-5 h-5" /> },
  ];

  const handleNav = (page: string) => {
    setCurrentPage(page);
    setIsOpen(false); // Close sidebar on mobile navigation
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex flex-col w-64 bg-slate-900 text-slate-100 border-r border-slate-800 transition-transform duration-300 lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand */}
        <div className="flex items-center gap-2 h-16 px-6 border-b border-slate-800">
          <div className="p-2 bg-indigo-600 rounded-lg text-white font-bold text-lg leading-none">
            HD
          </div>
          <div>
            <h1 className="font-semibold tracking-wide text-white">Help Desk</h1>
            <p className="text-xs text-slate-400">MCP Management System</p>
          </div>
        </div>

        {/* User Card */}
        {user && (
          <div className="px-6 py-4 border-b border-slate-800 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center font-semibold text-indigo-400">
              {user.username.substring(0, 2).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate">{user.username}</p>
              <div className="flex items-center gap-1 mt-0.5">
                {user.role === 'Admin' && <Shield className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />}
                <p className="text-xs text-slate-400 truncate">{user.role}</p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const isActive = currentPage === item.id || (item.id === 'tickets' && currentPage === 'ticket-detail');
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`flex items-center gap-3 w-full px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/10'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-100'
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer / Logout */}
        <div className="p-4 border-t border-slate-800">
          <button
            onClick={onLogout}
            className="flex items-center gap-3 w-full px-4 py-3 text-sm font-medium text-rose-400 hover:bg-rose-500/10 rounded-xl transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>
    </>
  );
};
