"use client";

import { CampaignList } from "@/components/campaigns/CampaignList";
import Link from "next/link";
import { Toaster } from "react-hot-toast";
import { motion } from "framer-motion";
import { FiPlus, FiBarChart2, FiTrendingUp } from "react-icons/fi";

export default function CampaignsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white py-10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="md:flex md:items-center md:justify-between"
        >
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3">
              <div className="bg-indigo-100 p-2 rounded-lg">
                <FiBarChart2 className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">
                  Campaigns
                </h1>
                <p className="mt-1 text-gray-600 text-sm">
                  Manage and track your influencer marketing campaigns
                </p>
              </div>
            </div>
          </div>
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="mt-4 flex md:ml-4 md:mt-0"
          >
            <Link
              href="/campaigns/create"
              className="inline-flex items-center rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 px-4 py-2.5 text-sm font-semibold text-white shadow-md hover:shadow-lg hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 relative overflow-hidden group"
            >
              <span className="absolute right-0 top-0 h-full w-12 translate-x-12 transform bg-white opacity-10 transition-all duration-1000 group-hover:translate-x-[-180px]"></span>
              <FiPlus className="mr-2 h-4 w-4" />
              Create Campaign
            </Link>
          </motion.div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-8"
        >
          <div className="bg-white rounded-xl shadow-xl border border-gray-100 p-6 overflow-hidden">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-100">
              <div className="flex items-center gap-2">
                <FiTrendingUp className="h-5 w-5 text-indigo-600" />
                <h2 className="text-lg font-medium text-gray-800">Active Campaigns</h2>
              </div>
              <div className="text-sm text-gray-500">
                Showing all campaigns
              </div>
            </div>
            <CampaignList />
          </div>
        </motion.div>
      </div>
      <Toaster position="top-right" />
    </main>
  );
}
// app/campaigns/page.tsx
'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import CampaignCard from '@/components/CampaignCard'
import CreateCampaignModal from '@/components/CreateCampaignModal'

interface Campaign {
  id: string;
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
        
        // Validate each campaign has an id
        const validCampaigns = campaignsList.filter(campaign => {
          if (!campaign.id) {
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
            campaign.id ? (
              <CampaignCard key={campaign.id} campaign={campaign} />
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