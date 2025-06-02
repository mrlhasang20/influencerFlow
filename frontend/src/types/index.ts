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
  campaign_name: string;
  brand_name: string;
  description: string;
  target_audience: string;
  budget_range: string;
  timeline: string;
  platforms: string[];
  content_types: string[];
  campaign_goals: string[];
  status: 'draft' | 'active' | 'completed';
  created_at: string;
  updated_at?: string;
  recommended_creators?: Array<{
    id: string;
    name: string;
    platform: string;
    followers: number;
    match_score: number;
  }>;
  outreach_messages?: Array<{
    creator_id: string;
    subject: string;
    status: string;
  }>;
  draft_contracts?: Array<{
    creator_id: string;
    status: string;
    payment_milestones?: Array<{
      percentage: number;
      description: string;
    }>;
  }>;
}

export interface SearchFilters {
  platform: string;
  category: string;
  minFollowers: number;
}
