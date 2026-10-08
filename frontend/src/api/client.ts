import { AnalysisRequest, AnalysisResponse, HealthResponse, ReadinessResponse } from '../types/api';

const rawBase = (import.meta.env.VITE_API_URL || '/api/v1').trim().replace(/\/+$/, '');
const API_BASE = rawBase.endsWith('/api/v1') ? rawBase : `${rawBase}/api/v1`;

class ApiClient {
  private getAuthToken(jobId: string): string | null {
    try {
      return sessionStorage.getItem(`claimlens_token_${jobId}`) || localStorage.getItem(`claimlens_token_${jobId}`);
    } catch {
      return null;
    }
  }

  private setAuthToken(jobId: string, token: string): void {
    try {
      sessionStorage.setItem(`claimlens_token_${jobId}`, token);
      localStorage.setItem(`claimlens_token_${jobId}`, token);
    } catch {
      // Ignore storage quota errors
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...((options.headers as Record<string, string>) || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // Fallback to generic message
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async submitAnalysis(req: AnalysisRequest): Promise<AnalysisResponse> {
    const data = await this.request<AnalysisResponse>('/analyses', {
      method: 'POST',
      body: JSON.stringify(req),
    });

    if (data.id && data.access_token) {
      this.setAuthToken(data.id, data.access_token);
    }

    return data;
  }

  async getAnalysis(id: string): Promise<AnalysisResponse> {
    const token = this.getAuthToken(id);
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return this.request<AnalysisResponse>(`/analyses/${id}`, {
      headers,
    });
  }

  async cancelAnalysis(id: string): Promise<void> {
    const token = this.getAuthToken(id);
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    await this.request(`/analyses/${id}/cancel`, {
      method: 'POST',
      headers,
    });
  }

  async deleteAnalysis(id: string): Promise<void> {
    const token = this.getAuthToken(id);
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    await this.request(`/analyses/${id}`, {
      method: 'DELETE',
      headers,
    });

    sessionStorage.removeItem(`claimlens_token_${id}`);
  }

  async checkHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async checkReadiness(): Promise<ReadinessResponse> {
    return this.request<ReadinessResponse>('/health/readiness');
  }
}

export const apiClient = new ApiClient();
