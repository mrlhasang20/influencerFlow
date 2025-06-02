"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import Link from "next/link";

interface Campaign {
  campaign_id: string;
  brand_name: string;
  campaign_name: string;
  status: string;
  created_at: string;
  creators_discovered: number;
  next_steps: string[];
  target_audience: string;
  budget_range: string;
  timeline: string;
  platforms: string[];
  content_types: string[];
  campaign_goals: string[];
  deliverables: Array<{
    type: string;
    description: string;
    quantity: number;
    due_date: string;
  }>;
  start_date: string;
  end_date: string;
  outreach_messages: Array<{
    creator: {
      name: string;
      platform: string;
      followers: number;
    };
    message: string;
    status: string;
  }>;
}

interface CampaignDetailsProps {
  campaignId: string;
}

export function CampaignDetails({ campaignId }: CampaignDetailsProps) {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCampaign = async () => {
      try {
        if (!campaignId) {
          throw new Error("Campaign ID is required");
        }

        const response = await axios.get(
          `http://localhost:8000/api/v1/campaigns/${campaignId}`
        );
        setCampaign(response.data);
      } catch (err) {
        console.error("Error fetching campaign:", err);
        setError("Failed to load campaign details. Please try again later.");
        toast.error("Failed to load campaign details");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCampaign();
  }, [campaignId]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || "Campaign not found"}</p>
        <Link
          href="/campaigns"
          className="mt-4 inline-flex items-center text-indigo-600 hover:text-indigo-500"
        >
          ← Back to Campaigns
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {campaign.campaign_name}
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                {campaign.brand_name}
              </p>
            </div>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              {campaign.status}
            </span>
          </div>
        </div>
      </div>

      {/* Campaign Details */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* General Information */}
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900">
              General Information
            </h2>
            <dl className="mt-4 space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Target Audience
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {campaign.target_audience}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Budget Range
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {campaign.budget_range}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Timeline</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {campaign.timeline}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Campaign Period
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(campaign.start_date).toLocaleDateString()} -{" "}
                  {new Date(campaign.end_date).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Campaign Goals & Platforms */}
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900">
              Campaign Details
            </h2>
            <div className="mt-4 space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Platforms</dt>
                <dd className="mt-1">
                  <div className="flex flex-wrap gap-2">
                    {campaign.platforms.map((platform) => (
                      <span
                        key={platform}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {platform}
                      </span>
                    ))}
                  </div>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Content Types
                </dt>
                <dd className="mt-1">
                  <div className="flex flex-wrap gap-2">
                    {campaign.content_types.map((type) => (
                      <span
                        key={type}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                      >
                        {type.replace("_", " ")}
                      </span>
                    ))}
                  </div>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Campaign Goals
                </dt>
                <dd className="mt-1">
                  <div className="flex flex-wrap gap-2">
                    {campaign.campaign_goals.map((goal) => (
                      <span
                        key={goal}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                      >
                        {goal.replace("_", " ")}
                      </span>
                    ))}
                  </div>
                </dd>
              </div>
            </div>
          </div>
        </div>

        {/* Deliverables */}
        <div className="bg-white shadow sm:rounded-lg lg:col-span-2">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900">Deliverables</h2>
            <div className="mt-4 space-y-4">
              {campaign.deliverables.map((deliverable, index) => (
                <div key={index} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        {deliverable.type}
                      </h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {deliverable.description}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        Quantity: {deliverable.quantity}
                      </p>
                      <p className="text-sm text-gray-500">
                        Due:{" "}
                        {new Date(deliverable.due_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Outreach Messages */}
        {campaign.outreach_messages &&
          campaign.outreach_messages.length > 0 && (
            <div className="bg-white shadow sm:rounded-lg lg:col-span-2">
              <div className="px-4 py-5 sm:p-6">
                <h2 className="text-lg font-medium text-gray-900">
                  Outreach Messages
                </h2>
                <div className="mt-4 space-y-4">
                  {campaign.outreach_messages.map((outreach, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-4 bg-gray-50"
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-sm font-medium text-gray-900">
                            {outreach.creator.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {outreach.creator.platform} •{" "}
                            {outreach.creator.followers.toLocaleString()}{" "}
                            followers
                          </p>
                          <p className="mt-2 text-sm text-gray-700">
                            {outreach.message}
                          </p>
                        </div>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          {outreach.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
      </div>

      {/* Back Button */}
      <div className="flex justify-start">
        <Link
          href="/campaigns"
          className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          ← Back to Campaigns
        </Link>
      </div>
    </div>
  );
}
