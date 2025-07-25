import { create } from 'zustand';
import { User } from './auth';
import { Report, ReportDetails } from './reports';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  clearAuth: () => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  
  setUser: (user: User) => {
    set({ user, isAuthenticated: true });
  },
  
  clearAuth: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
    }
    set({ user: null, isAuthenticated: false });
  },
  
  initializeAuth: () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      const userStr = localStorage.getItem('user');
      
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          set({ user, isAuthenticated: true });
        } catch (error) {
          console.error('Failed to parse user data:', error);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
      }
    }
  },
}));

// Dashboard Store
interface DashboardState {
  currentView: 'overview' | 'new-analysis' | 'reports' | 'rules' | 'profile';
  isLoading: boolean;
  reports: Report[];
  currentReport: ReportDetails | null;
  setCurrentView: (view: DashboardState['currentView']) => void;
  setLoading: (loading: boolean) => void;
  setReports: (reports: Report[]) => void;
  setCurrentReport: (report: ReportDetails | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  currentView: 'overview',
  isLoading: false,
  reports: [],
  currentReport: null,
  
  setCurrentView: (view) => set({ currentView: view }),
  setLoading: (loading) => set({ isLoading: loading }),
  setReports: (reports) => set({ reports }),
  setCurrentReport: (report) => set({ currentReport: report }),
}));