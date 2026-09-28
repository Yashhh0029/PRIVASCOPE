import axios from 'axios';
import {
  AuthResponse,
  User,
  Scan,
  ProtectionAction,
  DashboardStats,
  RecentScanItem,
  AuditLogItem,
  GatewayProvider,
  GatewayAnalyzeRequest,
  GatewayAnalyzeResponse,
  GatewayStats
} from '../types';

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('privascope_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 unauthenticated globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('privascope_token');
      localStorage.removeItem('privascope_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Health
  checkHealth: async () => {
    const res = await axios.get(`${API_BASE.replace('/api', '')}/health`);
    return res.data;
  },

  // Auth
  register: async (data: { name: string; email: string; password: string }): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/register', data);
    return res.data;
  },
  login: async (data: { email: string; password: string }): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/login', data);
    return res.data;
  },
  loginWithGoogle: async (idToken: string): Promise<AuthResponse> => {
    const res = await apiClient.post<AuthResponse>('/auth/google', {
      credential: idToken,
      id_token: idToken
    });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  // Documents
  uploadDocument: async (file: File): Promise<{ id: string; original_filename: string; file_type: string; file_size: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  getPreviewUrl: (docId: string, page: number = 1): string => {
    const token = localStorage.getItem('privascope_token');
    return `${API_BASE}/documents/${docId}/preview?page=${page}&token=${token}`;
  },

  // Scans
  scanDocument: async (docId: string, purpose?: string): Promise<Scan> => {
    const url = purpose ? `/scans/document/${docId}?purpose=${encodeURIComponent(purpose)}` : `/scans/document/${docId}`;
    const res = await apiClient.post<Scan>(url);
    return res.data;
  },
  scanText: async (text: string, purpose?: string): Promise<Scan> => {
    const url = purpose ? `/scans/text?purpose=${encodeURIComponent(purpose)}` : `/scans/text`;
    const res = await apiClient.post<Scan>(url, { text });
    return res.data;
  },
  getScan: async (scanId: string, purpose?: string): Promise<Scan> => {
    const url = purpose ? `/scans/${scanId}?purpose=${encodeURIComponent(purpose)}` : `/scans/${scanId}`;
    const res = await apiClient.get<Scan>(url);
    return res.data;
  },
  getScanStatus: async (scanId: string) => {
    const res = await apiClient.get(`/scans/${scanId}/status`);
    return res.data;
  },

  // Protection
  applyProtection: async (scanId: string, mode: 'MASK' | 'REDACT'): Promise<ProtectionAction> => {
    const res = await apiClient.post<ProtectionAction>(`/protection/${scanId}/apply`, { mode });
    return res.data;
  },
  downloadProtectedFile: async (actionId: string, filename: string) => {
    const response = await apiClient.get(`/protection/${actionId}/download`, {
      responseType: 'blob',
    });
    const blob = new Blob([response.data]);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  getDiff: async (scanId: string) => {
    const res = await apiClient.get(`/protection/${scanId}/diff`);
    return res.data;
  },

  // Dashboard & History
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get<DashboardStats>('/dashboard/stats');
    return res.data;
  },
  getHistory: async (page = 1, limit = 20): Promise<RecentScanItem[]> => {
    const res = await apiClient.get<RecentScanItem[]>(`/dashboard/history?page=${page}&limit=${limit}`);
    return res.data;
  },

  // Audit Logs
  getAuditLogs: async (page = 1, limit = 30): Promise<AuditLogItem[]> => {
    const res = await apiClient.get<AuditLogItem[]>(`/audit/logs?page=${page}&limit=${limit}`);
    return res.data;
  },

  // AI Privacy Gateway (Mode B)
  getGatewayProviders: async (): Promise<GatewayProvider[]> => {
    const res = await apiClient.get<GatewayProvider[]>('/gateway/providers');
    return res.data;
  },
  analyzePrompt: async (data: GatewayAnalyzeRequest): Promise<GatewayAnalyzeResponse> => {
    const res = await apiClient.post<GatewayAnalyzeResponse>('/gateway/analyze', data);
    return res.data;
  },
  rehydrateGatewayTokens: async (text: string, sessionId: string): Promise<{ session_id: string; rehydrated_text: string }> => {
    const res = await apiClient.post<{ session_id: string; rehydrated_text: string }>('/gateway/rehydrate', { text, session_id: sessionId });
    return res.data;
  },
  getGatewayStats: async (): Promise<GatewayStats> => {
    const res = await apiClient.get<GatewayStats>('/gateway/stats');
    return res.data;
  },
};
