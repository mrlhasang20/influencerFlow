"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FiSearch, FiFilter, FiUsers, FiThumbsUp } from "react-icons/fi";
import { CreatorCard } from "@/components/creators/CreatorCard";

interface SearchParams {
  query: string;
  platform: string;
  category: string;
  min_followers: number;
}

interface Creator {
  id: string;
  name: string;
  platform: string;
  category: string;
  followers: number;
  // Add more fields as needed based on the API response
}

export default function CreatorDiscovery() {
  const [searchParams, setSearchParams] = useState<SearchParams>({
    query: "",
    platform: "",
    category: "",
    min_followers: 0,
  });
  const [creators, setCreators] = useState<Creator[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [selectedCreator, setSelectedCreator] = useState<Creator | null>(null);
  
  // Sample images for creator cards
  const sampleImages = [
    '/placeholder-image-1.jpg',
    '/placeholder-image-2.jpg',
    '/placeholder-image-3.jpg',
    '/placeholder-image-4.jpg',
    '/placeholder-image-5.jpg',
  ];

  // Initialize with some example data when in development mode
  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && creators.length === 0) {
      // This is just for demo purposes, the actual API call will happen on search
      setCreators([
        { id: '1', name: 'Alex Fitness', platform: 'YouTube', category: 'Fitness', followers: 250000 },
        { id: '2', name: 'TechReviewer', platform: 'Instagram', category: 'Technology', followers: 125000 },
        { id: '3', name: 'CookWithMe', platform: 'TikTok', category: 'Food', followers: 500000 },
      ]);
    }
  }, [creators.length]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSelectedCreator(null);

    try {
      const response = await fetch("http://localhost:8000/discover/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch creators");
      }

      const data = await response.json();
      setCreators(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };
  
  const toggleFilters = () => {
    setFiltersOpen(!filtersOpen);
  };
  
  const handleCreatorSelect = (creator: Creator) => {
    setSelectedCreator(creator === selectedCreator ? null : creator);
  };

  return (
    <div className="py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Page Header */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 p-2 rounded-lg">
              <FiUsers className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Creator Discovery</h1>
              <p className="mt-1 text-gray-600 text-sm">Find the perfect creators for your next campaign</p>
            </div>
          </div>
          
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mt-4 md:mt-0 flex items-center space-x-2"
          >
            <button 
              onClick={toggleFilters}
              className="flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-indigo-600 bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-lg hover:from-indigo-100 hover:to-indigo-200 transition-all duration-200 shadow-sm"
            >
              <FiFilter className="h-4 w-4" />
              {filtersOpen ? 'Hide Filters' : 'Show Filters'}
            </button>
          </motion.div>
        </motion.div>

        {/* Search Form */}
        {filtersOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <form
              onSubmit={handleSearch}
              className="bg-white shadow-xl rounded-xl p-8 mb-10 border border-gray-100 relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-400 to-purple-500"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label
                    htmlFor="query"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Search Query
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiSearch className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      id="query"
                      value={searchParams.query}
                      onChange={(e) =>
                        setSearchParams({ ...searchParams, query: e.target.value })
                      }
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                      placeholder="e.g., fitness influencers in the US"
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="platform"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Platform
                  </label>
                  <select
                    id="platform"
                    value={searchParams.platform}
                    onChange={(e) =>
                      setSearchParams({ ...searchParams, platform: e.target.value })
                    }
                    className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                  >
                    <option value="">Select Platform</option>
                    <option value="Instagram">Instagram</option>
                    <option value="TikTok">TikTok</option>
                    <option value="YouTube">YouTube</option>
                    <option value="Twitter">Twitter</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Twitch">Twitch</option>
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="category"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Category
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiSearch className="h-4 w-4 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      id="category"
                      placeholder="e.g., fitness, beauty, tech"
                      className="mt-1 block w-full rounded-lg border border-gray-200 pl-10 px-4 py-2.5 shadow-sm bg-gray-50 hover:bg-white focus:bg-white transition-all duration-200 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      value={searchParams.category}
                      onChange={(e) =>
                        setSearchParams({ ...searchParams, category: e.target.value })
                      }
                    />
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="min_followers"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Minimum Followers
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiUsers className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="number"
                      id="min_followers"
                      value={searchParams.min_followers}
                      onChange={(e) =>
                        setSearchParams({
                          ...searchParams,
                          min_followers: parseInt(e.target.value) || 0,
                        })
                      }
                      className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                      min="0"
                      placeholder="Minimum follower count"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex flex-col sm:flex-row gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 font-medium text-sm transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center gap-2"
                >
                  <FiSearch className="h-4 w-4" />
                  {loading ? "Searching..." : "Search Creators"}
                </button>
                
                <button
                  type="button"
                  onClick={() => setSearchParams({
                    query: "",
                    platform: "",
                    category: "",
                    min_followers: 0,
                  })}
                  className="flex-1 sm:flex-initial bg-gray-100 text-gray-700 py-3 px-6 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 font-medium text-sm transition-all duration-200"
                >
                  Reset Filters
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* Error Message */}
        {error && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6"
          >
            {error}
          </motion.div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex justify-center my-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        )}

        {/* Results Section */}
        {!loading && (
          <>
            {creators.length > 0 ? (
              <>
                <div className="mb-6 flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-800">
                    {creators.length} Creator{creators.length !== 1 ? 's' : ''} Found
                  </h2>
                  <div className="text-sm text-gray-500">
                    Select a creator to see more details
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {creators.map((creator, index) => (
                    <motion.div
                      key={creator.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                      onClick={() => handleCreatorSelect(creator)}
                      className={`${selectedCreator === creator ? 'ring-2 ring-indigo-500 ring-opacity-50 rounded-[20px]' : ''}`}
                    >
                      <CreatorCard
                        id={creator.id}
                        name={creator.name}
                        role={creator.category}
                        avatar={`/placeholder-avatar-${(index % 4) + 1}.jpg`}
                        badgeCount={creator.followers}
                        badgeLabel="SMALL"
                        images={sampleImages}
                        category={creator.category}
                        description={`Influencer with ${creator.followers.toLocaleString()} followers on ${creator.platform}.`}
                      />
                      
                      {selectedCreator === creator && (
                        <motion.div 
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          transition={{ duration: 0.2 }}
                          className="mt-4 p-4 bg-white shadow-md rounded-lg border border-gray-100"
                        >
                          <div className="flex justify-between">
                            <button className="text-sm bg-gradient-to-r from-indigo-500 to-indigo-600 text-white py-1.5 px-3 rounded-lg hover:from-indigo-600 hover:to-indigo-700 transition-all duration-200 shadow-sm font-medium flex items-center gap-1.5">
                              <FiThumbsUp className="h-3.5 w-3.5" />
                              Add to Campaign
                            </button>
                            <button className="text-sm bg-gray-50 text-gray-700 py-1.5 px-3 rounded-lg hover:bg-gray-100 transition-all duration-200 shadow-sm font-medium flex items-center gap-1.5">
                              <FiUsers className="h-3.5 w-3.5" />
                              View Profile
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </>
            ) : (
              !loading && !error && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                  className="bg-white shadow-xl rounded-xl p-12 text-center my-12 border border-gray-100 relative overflow-hidden"
                >
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-400 to-purple-500"></div>
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    <div className="bg-indigo-50 p-4 rounded-full mb-6">
                      <FiSearch className="h-12 w-12 text-indigo-400" />
                    </div>
                    <h3 className="text-xl font-medium text-gray-700 mb-2">No creators found</h3>
                    <p className="max-w-md mx-auto mb-6">Try adjusting your search criteria or explore different categories to find the perfect creator match.</p>
                    <button 
                      onClick={() => setSearchParams({
                        query: "",
                        platform: "",
                        category: "",
                        min_followers: 0,
                      })}
                      className="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-lg hover:from-indigo-600 hover:to-indigo-700 transition-all duration-200 shadow-sm font-medium text-sm flex items-center gap-2"
                    >
                      <FiFilter className="h-4 w-4" />
                      Reset Filters
                    </button>
                  </div>
                </motion.div>
              )
            )}
          </>
        )}
      </div>
    </div>
  );
}
