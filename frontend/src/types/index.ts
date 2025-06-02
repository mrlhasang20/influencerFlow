export interface Creator {
  id: string;
  name: string;
  platform: string;
  followers: number;
  category: string;
  engagement_rate: number;
  profile_url?: string;
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  budget: number;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed';
  creators?: Creator[];
}

export interface SearchFilters {
  platform: string;
  category: string;
  minFollowers: number;
}
