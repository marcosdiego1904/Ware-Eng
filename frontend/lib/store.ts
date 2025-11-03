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
  currentView: 'overview' | 'new-analysis' | 'reports' | 'rule-center' | 'rules' | 'warehouse-settings' | 'profile' | 'action-center' | 'analytics' | 'track-wins' | 'location-intelligence';
  isLoading: boolean;
  reports: Report[];
  currentReport: ReportDetails | null;

  // Enhanced analysis state
  selectedRulesForAnalysis: number[];
  customRuleParameters: Record<number, any>;

  // Navigation state for cross-view communication
  actionCenterPreselectedCategory?: string;
  reportToOpen?: { reportId: number; tab?: 'business-intelligence' | 'analytics' };

  // Refresh trigger for overview data
  lastAnalysisTimestamp: number;

  // Pending report ID (set after upload, used to show processing UI)
  pendingReportId: number | null;

  setCurrentView: (view: DashboardState['currentView']) => void;
  setLoading: (loading: boolean) => void;
  setReports: (reports: Report[]) => void;
  setCurrentReport: (report: ReportDetails | null) => void;

  // Enhanced analysis actions
  setSelectedRulesForAnalysis: (ruleIds: number[]) => void;
  setCustomRuleParameters: (ruleId: number, parameters: any) => void;
  clearAnalysisSelection: () => void;

  // Navigation actions
  setActionCenterPreselectedCategory: (categoryId?: string) => void;
  setReportToOpen: (reportData?: { reportId: number; tab?: 'business-intelligence' | 'analytics' }) => void;

  // Refresh action
  triggerOverviewRefresh: () => void;

  // Pending report actions
  setPendingReportId: (reportId: number | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  currentView: 'overview',
  isLoading: false,
  reports: [],
  currentReport: null,

  // Enhanced analysis state
  selectedRulesForAnalysis: [],
  customRuleParameters: {},

  // Navigation state
  actionCenterPreselectedCategory: undefined,
  reportToOpen: undefined,

  // Refresh trigger
  lastAnalysisTimestamp: 0,

  // Pending report ID
  pendingReportId: null,

  setCurrentView: (view) => set({ currentView: view }),
  setLoading: (loading) => set({ isLoading: loading }),
  setReports: (reports) => set({ reports }),
  setCurrentReport: (report) => set({ currentReport: report }),

  // Enhanced analysis actions
  setSelectedRulesForAnalysis: (ruleIds) => set({ selectedRulesForAnalysis: ruleIds }),
  setCustomRuleParameters: (ruleId, parameters) =>
    set((state) => ({
      customRuleParameters: {
        ...state.customRuleParameters,
        [ruleId]: parameters
      }
    })),
  clearAnalysisSelection: () => set({
    selectedRulesForAnalysis: [],
    customRuleParameters: {}
  }),

  // Navigation actions
  setActionCenterPreselectedCategory: (categoryId) => set({ actionCenterPreselectedCategory: categoryId }),
  setReportToOpen: (reportData) => set({ reportToOpen: reportData }),

  // Refresh action - triggers overview to refetch data
  triggerOverviewRefresh: () => set({ lastAnalysisTimestamp: Date.now() }),

  // Pending report actions
  setPendingReportId: (reportId) => set({ pendingReportId: reportId }),
}));