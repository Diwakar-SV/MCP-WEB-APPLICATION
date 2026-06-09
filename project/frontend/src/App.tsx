import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { Toast } from './components/Toast';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { TicketList } from './pages/TicketList';
import { TicketDetail } from './pages/TicketDetail';
import { CreateTicket } from './pages/CreateTicket';
import { KnowledgeBase } from './pages/KnowledgeBase';
import type { User, ToastMessage } from './types';

export const App: React.FC = () => {
  // Authentication & session state
  const [token, setToken] = useState<string | null>(localStorage.getItem('ticket_auth_token'));
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('ticket_auth_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // UI state
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('ticket_theme') === 'dark';
  });
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Apply dark mode theme class to HTML element
  useEffect(() => {
    const root = window.document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      localStorage.setItem('ticket_theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('ticket_theme', 'light');
    }
  }, [darkMode]);

  const handleLoginSuccess = (accessToken: string, loggedInUser: User) => {
    localStorage.setItem('ticket_auth_token', accessToken);
    localStorage.setItem('ticket_auth_user', JSON.stringify(loggedInUser));
    setToken(accessToken);
    setUser(loggedInUser);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('ticket_auth_token');
    localStorage.removeItem('ticket_auth_user');
    setToken(null);
    setUser(null);
    setCurrentPage('dashboard');
    addToast('Signed out successfully.', 'info');
  };

  // Toast notifications helpers
  const addToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  // If not logged in, force Login Page view
  if (!token || !user) {
    return (
      <>
        <Login onLoginSuccess={handleLoginSuccess} addToast={addToast} />
        <Toast toasts={toasts} removeToast={removeToast} />
      </>
    );
  }

  // Router dispatcher
  const renderPageContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard token={token} addToast={addToast} />;
      case 'tickets':
        return (
          <TicketList
            token={token}
            currentUser={user}
            onSelectTicket={(id) => {
              setSelectedTicketId(id);
              setCurrentPage('ticket-detail');
            }}
            addToast={addToast}
          />
        );
      case 'ticket-detail':
        return (
          <TicketDetail
            ticketId={selectedTicketId!}
            token={token}
            currentUser={user}
            onBack={() => setCurrentPage('tickets')}
            addToast={addToast}
          />
        );
      case 'create-ticket':
        return (
          <CreateTicket
            token={token}
            onSuccess={() => setCurrentPage('tickets')}
            addToast={addToast}
          />
        );
      case 'kb':
        return <KnowledgeBase token={token} addToast={addToast} />;
      default:
        return <Dashboard token={token} addToast={addToast} />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-200">
      {/* Toast notifications drawer */}
      <Toast toasts={toasts} removeToast={removeToast} />

      {/* Main Sidebar */}
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        user={user}
        onLogout={handleLogout}
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
      />

      {/* Content wrapper */}
      <div className="flex flex-col flex-grow min-w-0 overflow-hidden">
        {/* Navigation Topbar */}
        <Topbar
          currentPage={currentPage}
          user={user}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        {/* Dynamic page contents wrapper */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/50 dark:bg-slate-950/40">
          <div className="max-w-7xl mx-auto">{renderPageContent()}</div>
        </main>
      </div>
    </div>
  );
};

export default App;
