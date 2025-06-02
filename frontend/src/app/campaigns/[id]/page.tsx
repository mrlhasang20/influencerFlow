'use client'

import { useQuery } from '@tanstack/react-query'
import { useParams, useRouter } from 'next/navigation'
import axios from 'axios'

interface Campaign {
  id: string;
  campaign_name: string;
  brand_name: string;
  description?: string;
  target_audience: string;
  budget_range: string;
  timeline: string;
  platforms: string[];
  content_types: string[];
  campaign_goals: string[];
  status: string;
  created_at: string;
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

export default function CampaignDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const campaignId = params?.id

  // Redirect to campaigns page if no ID is provided
  if (!campaignId) {
    router.push('/campaigns')
    return null
  }

  const { data: campaign, isLoading, error } = useQuery<Campaign>({
    queryKey: ['campaign', campaignId],
    queryFn: async () => {
      try {
        const { data } = await axios.get(`http://localhost:8000/api/v1/campaigns/${campaignId}`)
        return data
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          router.push('/campaigns')
        }
        throw error
      }
    },
    enabled: !!campaignId,
    retry: 1
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-red-600 text-lg">Error loading campaign details.</p>
        <button 
          onClick={() => router.push('/campaigns')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Return to Campaigns
        </button>
      </div>
    )
  }

  if (!campaign) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-600 text-lg">Campaign not found.</p>
        <button 
          onClick={() => router.push('/campaigns')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Return to Campaigns
        </button>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{campaign.campaign_name}</h1>
          <p className="text-lg text-gray-600 mt-2">{campaign.brand_name}</p>
        </div>
        <button
          onClick={() => router.push('/campaigns')}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
        >
          ← Back to Campaigns
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Campaign Overview */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Campaign Overview</h2>
          <dl className="space-y-4">
            <div>
              <dt className="font-medium text-gray-700">Description</dt>
              <dd className="mt-1 text-gray-600">{campaign.description}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Target Audience</dt>
              <dd className="mt-1 text-gray-600">{campaign.target_audience}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Budget Range</dt>
              <dd className="mt-1 text-gray-600">{campaign.budget_range}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Timeline</dt>
              <dd className="mt-1 text-gray-600">{campaign.timeline}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Platforms</dt>
              <dd className="mt-1 flex flex-wrap gap-2">
                {campaign.platforms?.map(platform => (
                  <span key={platform} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {platform}
                  </span>
                ))}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Content Types</dt>
              <dd className="mt-1 flex flex-wrap gap-2">
                {campaign.content_types?.map(type => (
                  <span key={type} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    {type}
                  </span>
                ))}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Campaign Goals</dt>
              <dd className="mt-1 flex flex-wrap gap-2">
                {campaign.campaign_goals?.map(goal => (
                  <span key={goal} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                    {goal.replace('_', ' ')}
                  </span>
                ))}
              </dd>
            </div>
          </dl>
        </div>

        {/* Selected Creators */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Selected Creators</h2>
          {campaign.recommended_creators && campaign.recommended_creators.length > 0 ? (
            <div className="space-y-4">
              {campaign.recommended_creators.map((creator) => (
                <div key={creator.id} className="border-b pb-4 last:border-0">
                  <h3 className="font-medium">{creator.name}</h3>
                  <p className="text-sm text-gray-600">
                    {creator.platform} • {creator.followers.toLocaleString()} followers
                  </p>
                  <p className="text-sm text-gray-600">
                    Match Score: {(creator.match_score * 100).toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">AI is analyzing to find the best creators for your campaign...</p>
          )}
        </div>

        {/* Campaign Progress */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Campaign Progress</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-700">Outreach Status</h3>
              {campaign.outreach_messages && campaign.outreach_messages.length > 0 ? (
                campaign.outreach_messages.map((message) => (
                  <div key={message.creator_id} className="mt-2 text-sm text-gray-600">
                    {message.status} - {message.subject}
                  </div>
                ))
              ) : (
                <p className="text-gray-500">Outreach will begin once creators are selected...</p>
              )}
            </div>
          </div>
        </div>

        {/* Payment Status */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Payment Status</h2>
          {campaign.draft_contracts && campaign.draft_contracts.length > 0 ? (
            <div className="space-y-4">
              {campaign.draft_contracts.map((contract) => (
                <div key={contract.creator_id} className="border-b pb-4 last:border-0">
                  <h3 className="font-medium">Creator #{contract.creator_id}</h3>
                  <p className="text-sm text-gray-600">Status: {contract.status}</p>
                  {contract.payment_milestones && (
                    <div className="mt-2">
                      <h4 className="text-sm font-medium text-gray-700">Payment Milestones:</h4>
                      {contract.payment_milestones.map((milestone, index) => (
                        <div key={index} className="text-sm text-gray-600">
                          {milestone.percentage}% - {milestone.description}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Payment details will be available after creator selection...</p>
          )}
        </div>
      </div>
    </div>
  )
}
