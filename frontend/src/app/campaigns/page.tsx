// app/campaigns/page.tsx
'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import CampaignCard from '@/components/CampaignCard'
import CreateCampaignModal from '@/components/CreateCampaignModal'

interface Campaign {
  campaign_id: string;
  campaign_name: string;
  brand_name: string;
  status: string;
  created_at: string;
  description?: string;
}

export default function CampaignsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

  const { data: campaigns = [], isLoading, error } = useQuery<Campaign[]>({
    queryKey: ['campaigns'],
    queryFn: async () => {
      try {
        const { data } = await axios.get('http://localhost:8000/api/v1/campaigns')
        console.log('Raw API Response:', data)
        
        // Ensure we're getting the campaigns array
        const campaignsList = data.campaigns || []
        console.log('Processed campaigns list:', campaignsList)
        
        // Validate each campaign has a campaign_id
        const validCampaigns = campaignsList.filter(campaign => {
          if (!campaign.campaign_id) {
            console.error('Campaign missing ID:', campaign)
            return false
          }
          return true
        })

        return validCampaigns
      } catch (error) {
        console.error('Error fetching campaigns:', error)
        throw error
      }
    },
    staleTime: 30000, // Cache for 30 seconds
    refetchOnWindowFocus: false
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-600 p-4">
        <p>Error loading campaigns. Please try again later.</p>
        <p className="text-sm mt-2">{(error as Error).message}</p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Create Campaign
        </button>
      </div>

      {!campaigns || campaigns.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p>No campaigns found. Create your first campaign!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {campaigns.map((campaign: Campaign) => (
            campaign.campaign_id ? (
              <CampaignCard key={campaign.campaign_id} campaign={campaign} />
            ) : null
          ))}
        </div>
      )}

      <CreateCampaignModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  )
}