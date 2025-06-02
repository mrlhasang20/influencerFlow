'use client'

import { useState, useCallback } from 'react';
import debounce from 'lodash/debounce';

interface SearchFilters {
  platform: string;
  minFollowers: number;
}

interface CreatorSearchProps {
  onSearch: (query: string) => void;
  onFilterChange: (filters: SearchFilters) => void;
  initialFilters: SearchFilters;
}

const PLATFORMS = ['Instagram', 'YouTube', 'TikTok', 'Twitter'];

export default function CreatorSearch({ onSearch, onFilterChange, initialFilters }: CreatorSearchProps) {
  const [searchValue, setSearchValue] = useState('');
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);

  const debouncedSearch = useCallback(
    debounce((value: string) => {
      onSearch(value);
    }, 300),
    []
  );

  const debouncedFilterChange = useCallback(
    debounce((newFilters: SearchFilters) => {
      onFilterChange(newFilters);
    }, 300),
    []
  );

  const handleSearchInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchValue(value);
    debouncedSearch(value);
  };

  const handleFilterUpdate = (newValues: Partial<SearchFilters>) => {
    const updatedFilters = { ...filters, ...newValues };
    setFilters(updatedFilters);
    debouncedFilterChange(updatedFilters);
  };

  return (
    <div className="space-y-4 bg-white p-4 rounded-lg shadow">
      <div className="relative">
        <input
          type="text"
          value={searchValue}
          placeholder="Search creators by name, category, engagement rate..."
          className="w-full p-2 pl-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          onChange={handleSearchInput}
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <select
          value={filters.platform}
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          onChange={(e) => handleFilterUpdate({ platform: e.target.value })}
        >
          <option value="">All Platforms</option>
          {PLATFORMS.map(platform => (
            <option key={platform} value={platform}>{platform}</option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Min Followers"
          value={filters.minFollowers || ''}
          className="p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          onChange={(e) => handleFilterUpdate({ 
            minFollowers: parseInt(e.target.value) || 0 
          })}
        />
      </div>
    </div>
  );
}
