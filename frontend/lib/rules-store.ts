/**
 * Zustand store for Warehouse Rules System
 * Extends the existing store pattern from store.ts
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { ruleManagementApi } from './rules-api';
import type {
  Rule,
  RuleCategory,
  RuleTemplate,
  RuleHistory,
  RuleFilters,
  RuleFormData,
  RulesViewState,
  RuleCreationStep,
  CreateRuleRequest,
  UpdateRuleRequest,
  ValidationResult,
  PreviewResult,
  PerformanceMetrics,
  AnalyticsData,
} from './rules-types';

// ==================== RULES STATE INTERFACE ====================

interface RulesState {
  // Data state
  rules: Rule[];
  categories: RuleCategory[];
  templates: RuleTemplate[];
  selectedRule: Rule | null;
  ruleHistory: RuleHistory[];
  
  // UI state
  viewState: RulesViewState;
  isLoading: boolean;
  isCreating: boolean;
  isEditing: boolean;
  isTesting: boolean;
  isValidating: boolean;
  
  // Filters and search
  filters: RuleFilters;
  searchQuery: string;
  filteredRules: Rule[];
  
  // Form state
  formData: Partial<RuleFormData>;
  validationErrors: Record<string, string>;
  validationResult: ValidationResult | null;
  previewResult: PreviewResult | null;
  currentStep: RuleCreationStep;
  
  // Performance data
  analytics: AnalyticsData | null;
  performanceMetrics: Record<number, PerformanceMetrics>;
  
  // Error handling
  error: string | null;
  lastError: Error | null;
  
  // ==================== UI ACTIONS ====================
  
  setCurrentSubView: (view: RulesViewState['currentSubView']) => void;
  setSelectedRule: (rule: Rule | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // ==================== FILTER ACTIONS ====================
  
  setFilters: (filters: Partial<RuleFilters>) => void;
  setSearchQuery: (query: string) => void;
  clearFilters: () => void;
  applyFilters: () => void;
  
  // ==================== FORM ACTIONS ====================
  
  setFormData: (data: Partial<RuleFormData>) => void;
  setValidationErrors: (errors: Record<string, string>) => void;
  setCurrentStep: (step: RuleCreationStep) => void;
  resetForm: () => void;
  validateForm: () => boolean;
  
  // ==================== API ACTIONS ====================
  
  // Data loading
  loadRules: () => Promise<void>;
  loadCategories: () => Promise<void>;
  loadTemplates: () => Promise<void>;
  loadRuleHistory: (ruleId: number) => Promise<void>;
  loadAnalytics: () => Promise<void>;
  
  // CRUD operations
  createRule: (data: CreateRuleRequest) => Promise<number>;
  updateRule: (id: number, data: UpdateRuleRequest) => Promise<void>;
  deleteRule: (id: number) => Promise<void>;
  duplicateRule: (id: number, newName: string) => Promise<number>;
  toggleRuleActivation: (id: number, isActive: boolean) => Promise<void>;
  
  // Testing and validation
  validateRule: (data: Partial<RuleFormData>) => Promise<ValidationResult>;
  previewRule: (data: Partial<RuleFormData>) => Promise<PreviewResult>;
  testRuleWithFile: (ruleId: number, file: File) => Promise<void>;
  
  // Performance
  loadRulePerformance: (ruleId: number) => Promise<void>;
  
  // Bulk operations
  bulkToggleRules: (ruleIds: number[], isActive: boolean) => Promise<void>;
  bulkDeleteRules: (ruleIds: number[]) => Promise<void>;
  
  // Templates
  createFromTemplate: (templateId: number, parameters: Record<string, unknown>, name: string) => Promise<number>;
}

// ==================== INITIAL STATE ====================

const initialState = {
  // Data
  rules: [],
  categories: [],
  templates: [],
  selectedRule: null,
  ruleHistory: [],
  
  // UI state
  viewState: {
    currentSubView: 'overview' as const,
    selectedRuleId: null,
    isCreating: false,
    isEditing: false
  },
  isLoading: false,
  isCreating: false,
  isEditing: false,
  isTesting: false,
  isValidating: false,
  
  // Filters
  filters: {
    status: 'all' as const
  },
  searchQuery: '',
  filteredRules: [],
  
  // Form
  formData: {
    priority: 'MEDIUM' as const,
    is_active: true,
    conditions: {},
    parameters: {}
  },
  validationErrors: {},
  validationResult: null,
  previewResult: null,
  currentStep: 'basic' as const,
  
  // Performance
  analytics: null,
  performanceMetrics: {},
  
  // Error handling
  error: null,
  lastError: null
};

// ==================== STORE IMPLEMENTATION ====================

export const useRulesStore = create<RulesState>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      // ==================== UI ACTIONS ====================
      
      setCurrentSubView: (view) => {
        set((state) => ({
          viewState: { ...state.viewState, currentSubView: view },
          error: null
        }));
      },
      
      setSelectedRule: (rule) => {
        set((state) => ({
          selectedRule: rule,
          viewState: {
            ...state.viewState,
            selectedRuleId: rule?.id || null,
            isEditing: false
          }
        }));
      },
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      setError: (error) => set({ error }),
      
      clearError: () => set({ error: null, lastError: null }),
      
      // ==================== FILTER ACTIONS ====================
      
      setFilters: (newFilters) => {
        set((state) => {
          const updatedFilters = { ...state.filters, ...newFilters };
          return { filters: updatedFilters };
        });
        get().applyFilters();
      },
      
      setSearchQuery: (query) => {
        set({ searchQuery: query });
        get().applyFilters();
      },
      
      clearFilters: () => {
        set({
          filters: { status: 'all' },
          searchQuery: ''
        });
        get().applyFilters();
      },
      
      applyFilters: () => {
        const { rules, filters, searchQuery } = get();
        let filtered = [...rules];
        
        // Apply status filter
        if (filters.status !== 'all') {
          filtered = filtered.filter(rule => 
            filters.status === 'active' ? rule.is_active : !rule.is_active
          );
        }
        
        // Apply category filter
        if (filters.category) {
          filtered = filtered.filter(rule => rule.category_name === filters.category);
        }
        
        // Apply priority filter
        if (filters.priority) {
          filtered = filtered.filter(rule => rule.priority === filters.priority);
        }
        
        // Apply rule type filter (system vs custom)
        if (filters.rule_type) {
          if (filters.rule_type === 'system') {
            filtered = filtered.filter(rule => rule.is_default);
          } else if (filters.rule_type === 'custom') {
            filtered = filtered.filter(rule => !rule.is_default);
          }
        }
        
        // Apply search query
        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase();
          filtered = filtered.filter(rule =>
            rule.name.toLowerCase().includes(query) ||
            rule.description.toLowerCase().includes(query) ||
            rule.rule_type.toLowerCase().includes(query) ||
            rule.category_name.toLowerCase().includes(query)
          );
        }
        
        set({ filteredRules: filtered });
      },
      
      // ==================== FORM ACTIONS ====================
      
      setFormData: (data) => {
        set((state) => ({
          formData: { ...state.formData, ...data },
          validationErrors: {} // Clear validation errors when form changes
        }));
      },
      
      setValidationErrors: (errors) => set({ validationErrors: errors }),
      
      setCurrentStep: (step) => set({ currentStep: step }),
      
      resetForm: () => {
        set({
          formData: {
            priority: 'MEDIUM',
            is_active: true,
            conditions: {},
            parameters: {}
          },
          validationErrors: {},
          validationResult: null,
          previewResult: null,
          currentStep: 'basic'
        });
      },
      
      validateForm: () => {
        const { formData } = get();
        const errors: Record<string, string> = {};
        
        // Basic validation
        if (!formData.name?.trim()) {
          errors.name = 'Rule name is required';
        }
        
        if (!formData.description?.trim()) {
          errors.description = 'Rule description is required';
        }
        
        if (!formData.category_id) {
          errors.category_id = 'Category is required';
        }
        
        if (!formData.rule_type?.trim()) {
          errors.rule_type = 'Rule type is required';
        }
        
        // Conditions validation - only for non-default rules
        if (!formData.conditions || Object.keys(formData.conditions).length === 0) {
          errors.conditions = 'At least one condition is required';
        } else {
          // Additional validation: check if conditions have actual values
          const hasValidConditions = Object.entries(formData.conditions).some(([key, value]) => {
            if (key === 'rule_type') return false; // Skip rule_type field
            return value !== null && value !== undefined && value !== '';
          });
          
          if (!hasValidConditions) {
            errors.conditions = 'Conditions must have valid values';
          }
        }
        
        set({ validationErrors: errors });
        return Object.keys(errors).length === 0;
      },
      
      // ==================== API ACTIONS ====================
      
      loadRules: async () => {
        try {
          set({ isLoading: true, error: null });
          const { filters } = get();
          const response = await ruleManagementApi.rules.getRules(filters);
          
          if (response.success) {
            const parsedRules = response.rules.map(rule => {
              const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
              const parameters = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
              return {
                ...rule,
                conditions: conditions || {},
                parameters: parameters || {},
              };
            });
            set({ rules: parsedRules });
            get().applyFilters();
          } else {
            throw new Error('Failed to load rules');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          console.error('Error loading rules:', error);
        } finally {
          set({ isLoading: false });
        }
      },
      
      loadCategories: async () => {
        try {
          const response = await ruleManagementApi.categories.getCategories();
          if (response.success) {
            set({ categories: response.categories });
          }
        } catch (error) {
          console.error('Error loading categories:', error);
        }
      },
      
      loadTemplates: async () => {
        try {
          const response = await ruleManagementApi.templates.getTemplates();
          if (response.success) {
            set({ templates: response.templates });
          }
        } catch (error) {
          console.error('Error loading templates:', error);
        }
      },
      
      loadRuleHistory: async (ruleId: number) => {
        try {
          const response = await ruleManagementApi.history.getRuleHistory(ruleId);
          if (response.success) {
            set({ ruleHistory: response.history });
          }
        } catch (error) {
          console.error('Error loading rule history:', error);
        }
      },
      
      loadAnalytics: async () => {
        try {
          const response = await ruleManagementApi.performance.getAnalytics();
          if (response.success) {
            set({ analytics: response });
          }
        } catch (error) {
          console.error('Error loading analytics:', error);
        }
      },
      
      createRule: async (data: CreateRuleRequest) => {
        try {
          set({ isCreating: true, error: null });
          const response = await ruleManagementApi.rules.createRule(data);
          
          if (response.success && response.rule) {
            const rule = response.rule;
            const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
            const parameters = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
            const newRule = {
              ...rule,
              conditions: conditions || {},
              parameters: parameters || {},
            };

            // Add new rule to the list
            set((state) => ({
              rules: [newRule, ...state.rules]
            }));
            
            get().applyFilters();
            get().resetForm();
            
            return newRule.id;
          } else {
            throw new Error('Failed to create rule');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isCreating: false });
        }
      },
      
      updateRule: async (id: number, data: UpdateRuleRequest) => {
        try {
          set({ isEditing: true, error: null });
          console.log('Store: Updating rule', id, 'with data:', data);
          
          const response = await ruleManagementApi.rules.updateRule(id, data);
          console.log('Store: Update response:', response);
          
          if (response.success && response.rule) {
            const rule = response.rule;
            const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
            const parameters = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
            const updatedRule = {
              ...rule,
              conditions: conditions || {},
              parameters: parameters || {},
            };

            // Update rule in the list
            set((state) => ({
              rules: state.rules.map(rule => 
                rule.id === id ? updatedRule : rule
              ),
              selectedRule: state.selectedRule?.id === id ? updatedRule : state.selectedRule
            }));
            
            get().applyFilters();
          } else {
            throw new Error(response.message || 'Failed to update rule');
          }
        } catch (error) {
          console.error('Store: Rule update error:', error);
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isEditing: false });
        }
      },
      
      deleteRule: async (id: number) => {
        try {
          set({ error: null });
          const response = await ruleManagementApi.rules.deleteRule(id);
          
          if (response.success) {
            // Remove rule from the list
            set((state) => ({
              rules: state.rules.filter(rule => rule.id !== id),
              selectedRule: state.selectedRule?.id === id ? null : state.selectedRule
            }));
            
            get().applyFilters();
          } else {
            throw new Error(response.message || 'Failed to delete rule');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        }
      },
      
      duplicateRule: async (id: number, newName: string) => {
        try {
          set({ error: null });
          const response = await ruleManagementApi.rules.duplicateRule(id, newName);
          
          if (response.success && response.rule) {
            const rule = response.rule;
            const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
            const parameters = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
            const newRule = {
              ...rule,
              conditions: conditions || {},
              parameters: parameters || {},
            };

            // Add duplicated rule to the list
            set((state) => ({
              rules: [newRule, ...state.rules]
            }));
            
            get().applyFilters();
            return newRule.id;
          } else {
            throw new Error('Failed to duplicate rule');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        }
      },
      
      toggleRuleActivation: async (id: number, isActive: boolean) => {
        try {
          set({ error: null });
          const response = await ruleManagementApi.rules.toggleRuleActivation(id, isActive);
          
          if (response.success && response.rule) {
            const rule = response.rule;
            const conditions = typeof rule.conditions === 'string' ? JSON.parse(rule.conditions) : rule.conditions;
            const parameters = typeof rule.parameters === 'string' ? JSON.parse(rule.parameters) : rule.parameters;
            const updatedRule = {
              ...rule,
              conditions: conditions || {},
              parameters: parameters || {},
            };

            // Update rule in the list
            set((state) => ({
              rules: state.rules.map(rule => 
                rule.id === id ? updatedRule : rule
              ),
              selectedRule: state.selectedRule?.id === id ? updatedRule : state.selectedRule
            }));
            
            get().applyFilters();
          } else {
            throw new Error('Failed to toggle rule activation');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        }
      },
      
      validateRule: async (data: Partial<RuleFormData>) => {
        try {
          set({ isValidating: true, error: null });
          const response = await ruleManagementApi.testing.validateRule({
            conditions: JSON.stringify(data.conditions || {}),
            rule_type: data.rule_type
          });
          
          set({ validationResult: response });
          return response;
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isValidating: false });
        }
      },
      
      previewRule: async (data: Partial<RuleFormData>) => {
        try {
          set({ isValidating: true, error: null });
          const response = await ruleManagementApi.testing.previewRule({
            name: data.name,
            rule_type: data.rule_type || 'STAGNANT_PALLETS',
            conditions: data.conditions || {},
            parameters: data.parameters,
            priority: data.priority
          });
          
          set({ previewResult: response });
          return response;
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isValidating: false });
        }
      },
      
      testRuleWithFile: async (ruleId: number, file: File) => {
        try {
          set({ isTesting: true, error: null });
          const response = await ruleManagementApi.testing.testRules({
            test_file: file,
            rule_ids: [ruleId]
          });
          
          if (!response.success) {
            throw new Error('Rule test failed');
          }
          
          // Handle test results (could show in a modal or update UI)
          console.log('Test results:', response.test_results);
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isTesting: false });
        }
      },
      
      loadRulePerformance: async (ruleId: number) => {
        try {
          const response = await ruleManagementApi.performance.getRulePerformance(ruleId);
          if (response.success) {
            set((state) => ({
              performanceMetrics: {
                ...state.performanceMetrics,
                [ruleId]: response
              }
            }));
          }
        } catch (error) {
          console.error('Error loading rule performance:', error);
        }
      },
      
      bulkToggleRules: async (ruleIds: number[], isActive: boolean) => {
        try {
          set({ error: null });
          const response = await ruleManagementApi.bulk.bulkToggleRules(ruleIds, isActive);
          
          if (response.success) {
            // Reload rules to get updated state
            await get().loadRules();
          } else {
            throw new Error(`Failed to update ${response.errors.length} rules`);
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        }
      },
      
      bulkDeleteRules: async (ruleIds: number[]) => {
        try {
          set({ error: null });
          const response = await ruleManagementApi.bulk.bulkDeleteRules(ruleIds);
          
          if (response.success) {
            // Remove deleted rules from the list
            set((state) => ({
              rules: state.rules.filter(rule => !ruleIds.includes(rule.id)),
              selectedRule: ruleIds.includes(state.selectedRule?.id || 0) ? null : state.selectedRule
            }));
            
            get().applyFilters();
          } else {
            throw new Error(`Failed to delete ${response.errors.length} rules`);
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        }
      },
      
      createFromTemplate: async (templateId: number, parameters: Record<string, unknown>, name: string) => {
        try {
          set({ isCreating: true, error: null });
          const response = await ruleManagementApi.templates.createFromTemplate(templateId, {
            template_id: templateId,
            template_name: '',
            parameters,
            rule_name: name
          });
          
          if (response.success && response.rule) {
            // Add new rule to the list
            set((state) => ({
              rules: [response.rule, ...state.rules]
            }));
            
            get().applyFilters();
            return response.rule.id;
          } else {
            throw new Error('Failed to create rule from template');
          }
        } catch (error) {
          const errorMessage = ruleManagementApi.getErrorMessage(error);
          set({ error: errorMessage, lastError: error as Error });
          throw error;
        } finally {
          set({ isCreating: false });
        }
      }
    }),
    {
      name: 'rules-store', // name for devtools
      partialize: (state: RulesState) => ({
        // Only persist certain parts of the state
        filters: state.filters,
        viewState: state.viewState
      })
    }
  )
);

// ==================== SELECTORS ====================

// Selector hooks for computed values
export const useFilteredRules = () => useRulesStore((state) => state.filteredRules || []);
export const useActiveRules = () => useRulesStore((state) => (state.rules || []).filter(r => r.is_active));
export const useRulesByCategory = () => useRulesStore((state) => {
  const rules = state.filteredRules || [];
  const grouped: Record<string, Rule[]> = {};
  
  rules.forEach(rule => {
    const categoryName = rule.category_name || 'Uncategorized';
    if (!grouped[categoryName]) {
      grouped[categoryName] = [];
    }
    grouped[categoryName].push(rule);
  });
  
  return grouped;
});

export const useRulesStats = () => useRulesStore((state) => {
  const rules = state.rules || [];
  return {
    total: rules.length,
    active: rules.filter(r => r.is_active).length,
    inactive: rules.filter(r => !r.is_active).length,
    custom: rules.filter(r => !r.is_default).length,
    default: rules.filter(r => r.is_default).length
  };
});

export const useCurrentRule = () => useRulesStore((state) => state.selectedRule);
export const useRulesViewState = () => useRulesStore((state) => state.viewState);
export const useRulesFormState = () => useRulesStore((state) => ({
  formData: state.formData,
  validationErrors: state.validationErrors,
  currentStep: state.currentStep,
  isValidating: state.isValidating,
  validationResult: state.validationResult,
  previewResult: state.previewResult
}));