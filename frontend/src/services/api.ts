import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Paper {
  id: number;
  pubmed_id: string;
  title: string;
  abstract?: string;
  authors: string[];
  journal: string;
  publication_date?: string;
  summary?: string;
  themes?: string[];
  sentiment_score?: number;
  complexity_score?: number;
}

export interface SearchRequest {
  query: string;
  max_results: number;
}

export const paperService = {
  getPapers: async (skip: number = 0, limit: number = 20, theme?: string): Promise<Paper[]> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (theme) params.append('theme', theme);
    
    const response = await api.get(`/papers?${params}`);
    return response.data;
  },

  getPaper: async (paperId: number): Promise<Paper> => {
    const response = await api.get(`/papers/${paperId}`);
    return response.data;
  },

  searchPapers: async (searchRequest: SearchRequest): Promise<any> => {
    const response = await api.post('/papers/search', searchRequest);
    return response.data;
  },
};

export default api;