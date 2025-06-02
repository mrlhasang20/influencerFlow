"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";
import { CampaignCard } from "./CampaignCard";
import { ModernCampaignCard } from "./ModernCampaignCard";
import toast from "react-hot-toast";

interface Campaign {
  campaign_id: string;
  brand_name: string;
  campaign_name: string;
  status: string;
  created_at: string;
  creators_discovered: number;
  next_steps: string[];
}

export function CampaignList() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useModernDesign, setUseModernDesign] = useState(true);
  
  // Sample images for cards
  const sampleImages = [
    '/placeholder-image-1.jpg',
    '/placeholder-image-2.jpg',
    '/placeholder-image-3.jpg',
    '/placeholder-image-4.jpg',
    '/placeholder-image-5.jpg',
  ];

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/v1/campaigns"
        );
        setCampaigns(response.data.campaigns || []);
      } catch (err) {
        console.error("Error fetching campaigns:", err);
        setError("Failed to load campaigns. Please try again later.");
        toast.error("Failed to load campaigns");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 text-indigo-600 hover:text-indigo-500"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (campaigns.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">No campaigns yet</h3>
        <p className="mt-2 text-sm text-gray-500">
          Get started by creating your first campaign
        </p>
        <div className="mt-6">
          <Link
            href="/campaigns/create"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Create Campaign
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-end mb-6">
        <div className="inline-flex items-center rounded-lg bg-gray-100 p-1">
          <button
            onClick={() => setUseModernDesign(false)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md ${
              !useModernDesign
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Classic
          </button>
          <button
            onClick={() => setUseModernDesign(true)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md ${
              useModernDesign
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Modern
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {campaigns.map((campaign, index) => (
          <div key={campaign.campaign_id}>
            {useModernDesign ? (
              <ModernCampaignCard
                id={campaign.campaign_id}
                name={campaign.brand_name}
                brand={campaign.campaign_name}
                avatar={`/placeholder-avatar-${(index % 4) + 1}.jpg`}
                statValue={campaign.creators_discovered || 0}
                badgeLabel={campaign.status}
                category="Collaborative project"
                description={`Campaign created on ${new Date(campaign.created_at).toLocaleDateString()}`}
                onClick={() => window.location.href = `/campaigns/${campaign.campaign_id}`}
              />
            ) : (
              <Link href={`/campaigns/${campaign.campaign_id}`} className="block">
                <CampaignCard campaign={campaign} />
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
