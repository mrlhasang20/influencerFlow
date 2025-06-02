'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import CreatorCard from '@/components/CreatorCard'
import CreatorSearch from '@/components/CreatorSearch'
import LoadingSpinner from '@/components/LoadingSpinner'

interface Creator {
  creator_id: string;
  name: string;
  handle: string;
  platform: string;
  followers: number;
  engagement_rate: number;
  categories: string[];
  location?: string;
  content_style?: string;
  match_score?: number;
}

interface SearchFilters {
  platform: string;
  minFollowers: number;
}

interface SearchResponse {
  results: Creator[];
  total_found: number;
  query: string;
  search_time_ms?: number;
  used_cache: boolean;
  filters_applied?: Record<string, any>;
  error_message?: string;
}

const initialFilters: SearchFilters = {
  platform: '',
  minFollowers: 0
};

export default function CreatorsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<SearchFilters>(initialFilters)

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['creators', searchQuery, filters],
    queryFn: async () => {
      try {
        console.log('Sending search request:', {
          query: searchQuery,
          filters
        });

        const { data } = await axios.post<SearchResponse>('http://localhost:8000/api/v1/creators/search', {
          query: searchQuery.trim(),
          filters: filters.platform || filters.minFollowers > 0 ? filters : undefined
        });

        console.log('Received response:', data);

        // Ensure we properly map the response
        return {
          ...data,
          results: data.results.map(creator => ({
            ...creator,
            creator_id: creator.creator_id || creator.id,
            categories: Array.isArray(creator.categories) ? creator.categories : [],
            engagement_rate: typeof creator.engagement_rate === 'number' ? creator.engagement_rate * 100 : 0,
            followers: typeof creator.followers === 'number' ? creator.followers : 0
          }))
        };
      } catch (error) {
        console.error('Search error:', error);
        throw error;
      }
    },
    staleTime: 30000,
    refetchOnWindowFocus: false,
    retry: 1
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleFilterChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">Discover Creators</h1>
        <CreatorSearch
          onSearch={handleSearch}
          onFilterChange={handleFilterChange}
          initialFilters={initialFilters}
        />
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="text-red-600 p-4">
          Error loading creators. Please try again.
          <pre className="mt-2 text-sm">
            {error instanceof Error ? error.message : 'Unknown error'}
          </pre>
        </div>
      ) : (
        <div>
          {(!response?.results || response.results.length === 0) ? (
            <div className="text-center py-12">
              <div className="text-xl font-semibold text-gray-700 mb-4">
                No Creators Found
              </div>
              <div className="text-gray-600 max-w-2xl mx-auto px-4">
                {response?.error_message ? (
                  <p className="text-lg">{response.error_message}</p>
                ) : (
                  <p className="text-lg">
                    No creators found matching your search criteria. Try adjusting your search or filters.
                  </p>
                )}
                {response?.filters_applied && Object.keys(response.filters_applied).length > 0 && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <div className="font-medium text-gray-700">Applied Filters:</div>
                    <ul className="mt-2 space-y-1 text-gray-500">
                      {Object.entries(response.filters_applied).map(([key, value]) => (
                        <li key={key} className="flex items-center justify-center space-x-2">
                          <span className="font-medium">{key.replace(/_/g, ' ')}:</span>
                          <span>{Array.isArray(value) ? value.join(', ') : value}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {response.results.map((creator: Creator) => (
                <CreatorCard
                  key={creator.creator_id}
                  creator={creator}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
