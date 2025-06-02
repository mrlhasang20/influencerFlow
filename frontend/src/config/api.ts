export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  creators: {
    search: `${API_BASE_URL}/creators/search`,
    list: `${API_BASE_URL}/creators`,
  },
  campaigns: {
    list: `${API_BASE_URL}/campaigns`,
    create: `${API_BASE_URL}/campaigns`,
    update: (id: string) => `${API_BASE_URL}/campaigns/${id}`,
    delete: (id: string) => `${API_BASE_URL}/campaigns/${id}`,
  }
};
