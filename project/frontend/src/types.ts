export interface User {
  id: number;
  username: string;
  email: string;
  role: 'User' | 'Admin';
}

export interface Comment {
  id: number;
  ticket_id: number;
  comment: string;
  author: string;
  created_at: string;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  created_at: string;
  updated_at: string;
  created_by: number;
  creator: User;
  comments: Comment[];
}

export interface KBArticle {
  id: number;
  question: string;
  answer: string;
  category: string;
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface DayCount {
  date: string;
  count: number;
}

export interface DashboardStats {
  total_tickets: number;
  open_tickets: number;
  resolved_tickets: number;
  high_priority_tickets: number;
  status_distribution: StatusCount[];
  tickets_per_day: DayCount[];
}

export interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}
