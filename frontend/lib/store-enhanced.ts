import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { User } from './auth';
import { Report, ReportDetails, Anomaly } from './reports';

// Toast notification types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
}

// Loading state for different operations
export interface LoadingState {
  [key: string]: boolean;
}

// Error state management
export interface ErrorState {
  [key: string]: string | null;
}

// Enhanced Auth State
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  setUser: (user: User) => void;
  clearAuth: () => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isInitialized: false,
      
      setUser: (user: User) => {
        set({ user, isAuthenticated: true, isInitialized: true });
      },
      
      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
        set({ user: null, isAuthenticated: false, isInitialized: true });
      },
      
      initializeAuth: () => {
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('auth_token');
          const userStr = localStorage.getItem('user');
          
          if (token && userStr) {
            try {
              const user = JSON.parse(userStr);
              set({ user, isAuthenticated: true, isInitialized: true });
            } catch (error) {
              console.error('Failed to parse user data:', error);
              localStorage.removeItem('auth_token');
              localStorage.removeItem('user');
              set({ user: null, isAuthenticated: false, isInitialized: true });
            }
          } else {
            set({ isInitialized: true });
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);

// Enhanced Dashboard Store
interface DashboardState {
  // Navigation
  currentView: 'overview' | 'new-analysis' | 'reports' | 'rules' | 'profile' | 'analytics';
  previousView: DashboardState['currentView'] | null;
  
  // Data
  reports: Report[];
  currentReport: ReportDetails | null;
  recentReports: Report[];
  
  // Loading states
  loadingStates: LoadingState;
  
  // Error states
  errors: ErrorState;
  
  // UI preferences
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  
  // Actions
  setCurrentView: (view: DashboardState['currentView']) => void;
  goBack: () => void;
  setLoading: (key: string, loading: boolean) => void;
  setError: (key: string, error: string | null) => void;
  setReports: (reports: Report[]) => void;
  setCurrentReport: (report: ReportDetails | null) => void;
  updateReport: (reportId: number, updates: Partial<ReportDetails>) => void;
  updateAnomaly: (reportId: number, anomalyId: number, updates: Partial<Anomaly>) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  clearErrors: () => void;
  isLoading: (key: string) => boolean;
  getError: (key: string) => string | null;
}

export const useDashboardStore = create<DashboardState>()(
  subscribeWithSelector(
    persist(
      (set, get) => ({
        // Initial state
        currentView: 'overview',
        previousView: null,
        reports: [],
        currentReport: null,
        recentReports: [],
        loadingStates: {},
        errors: {},
        sidebarCollapsed: false,
        theme: 'light',
        
        // Navigation actions
        setCurrentView: (view) => {
          const currentView = get().currentView;
          set({ 
            currentView: view, 
            previousView: currentView,
            // Clear errors when navigating
            errors: {}
          });
        },
        
        goBack: () => {
          const { previousView } = get();
          if (previousView) {
            set({ currentView: previousView, previousView: null });
          }
        },
        
        // Loading state management
        setLoading: (key, loading) => {
          set((state) => ({
            loadingStates: {
              ...state.loadingStates,
              [key]: loading
            }
          }));
        },
        
        isLoading: (key) => {
          return get().loadingStates[key] || false;
        },
        
        // Error state management
        setError: (key, error) => {
          set((state) => ({
            errors: {
              ...state.errors,
              [key]: error
            }
          }));
        },
        
        getError: (key) => {
          return get().errors[key] || null;
        },
        
        clearErrors: () => {
          set({ errors: {} });
        },
        
        // Data management
        setReports: (reports) => {
          const recentReports = reports.slice(0, 5);
          set({ reports, recentReports });
        },
        
        setCurrentReport: (report) => {
          set({ currentReport: report });
        },
        
        updateReport: (reportId, updates) => {
          set((state) => {
            const updatedReports = state.reports.map(report => 
              report.id === reportId ? { ...report, ...updates } : report
            );
            
            const updatedCurrentReport = state.currentReport?.reportId === reportId
              ? { ...state.currentReport, ...updates }
              : state.currentReport;
            
            return {
              reports: updatedReports,
              currentReport: updatedCurrentReport,
              recentReports: updatedReports.slice(0, 5)
            };
          });
        },
        
        updateAnomaly: (reportId, anomalyId, updates) => {
          set((state) => {
            if (state.currentReport?.reportId === reportId) {
              const updatedLocations = state.currentReport.locations.map(location => ({
                ...location,
                anomalies: location.anomalies.map(anomaly => 
                  anomaly.id === anomalyId ? { ...anomaly, ...updates } : anomaly
                )
              }));
              
              return {
                currentReport: {
                  ...state.currentReport,
                  locations: updatedLocations
                }
              };
            }
            return state;
          });
        },
        
        // UI preferences
        setSidebarCollapsed: (collapsed) => {
          set({ sidebarCollapsed: collapsed });
        },
        
        setTheme: (theme) => {
          set({ theme });
          // Apply theme to document root
          if (typeof window !== 'undefined') {
            document.documentElement.classList.toggle('dark', theme === 'dark');
          }
        },
      }),
      {
        name: 'dashboard-storage',
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          theme: state.theme,
          // Don't persist sensitive data
        }),
      }
    )
  )
);

// Toast Store
interface ToastState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  
  addToast: (toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    
    set((state) => ({
      toasts: [...state.toasts, newToast]
    }));
    
    // Auto-remove toast after duration
    const duration = toast.duration || 5000;
    if (duration > 0) {
      setTimeout(() => {
        get().removeToast(id);
      }, duration);
    }
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter(toast => toast.id !== id)
    }));
  },
  
  clearToasts: () => {
    set({ toasts: [] });
  },
}));

// Analytics Store for performance tracking
interface AnalyticsState {
  pageViews: Record<string, number>;
  actionCounts: Record<string, number>;
  lastActivity: Date | null;
  sessionStart: Date | null;
  
  trackPageView: (page: string) => void;
  trackAction: (action: string) => void;
  updateActivity: () => void;
  getSessionDuration: () => number;
}

export const useAnalyticsStore = create<AnalyticsState>((set, get) => ({
  pageViews: {},
  actionCounts: {},
  lastActivity: null,
  sessionStart: new Date(),
  
  trackPageView: (page) => {
    set((state) => ({
      pageViews: {
        ...state.pageViews,
        [page]: (state.pageViews[page] || 0) + 1
      },
      lastActivity: new Date()
    }));
  },
  
  trackAction: (action) => {
    set((state) => ({
      actionCounts: {
        ...state.actionCounts,
        [action]: (state.actionCounts[action] || 0) + 1
      },
      lastActivity: new Date()
    }));
  },
  
  updateActivity: () => {
    set({ lastActivity: new Date() });
  },
  
  getSessionDuration: () => {
    const { sessionStart } = get();
    if (!sessionStart) return 0;
    return Date.now() - sessionStart.getTime();
  },
}));

// Utility hooks for common patterns
export const useLoadingState = (key: string) => {
  const { isLoading, setLoading } = useDashboardStore();
  return {
    loading: isLoading(key),
    setLoading: (loading: boolean) => setLoading(key, loading)
  };
};

export const useErrorState = (key: string) => {
  const { getError, setError } = useDashboardStore();
  return {
    error: getError(key),
    setError: (error: string | null) => setError(key, error)
  };
};

export const useToast = () => {
  const { addToast } = useToastStore();
  
  return {
    success: (title: string, description?: string) => 
      addToast({ type: 'success', title, description }),
    error: (title: string, description?: string) => 
      addToast({ type: 'error', title, description }),
    warning: (title: string, description?: string) => 
      addToast({ type: 'warning', title, description }),
    info: (title: string, description?: string) => 
      addToast({ type: 'info', title, description }),
  };
};