// components/CreateCampaignModal.tsx
'use client'
import { Dialog } from '@headlessui/react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

const campaignSchema = z.object({
  brand_name: z.string().min(1, "Brand name is required"),
  campaign_name: z.string().min(1, "Campaign name is required"),
  description: z.string().min(1, "Description is required"),
  target_audience: z.string().min(1, "Target audience is required"),
  budget_range: z.string().min(1, "Budget range is required"),
  timeline: z.string().min(1, "Timeline is required"),
  platforms: z.array(z.string()).min(1, "Select at least one platform"),
  content_types: z.array(z.string()).min(1, "Select at least one content type"),
  campaign_goals: z.array(z.string()).min(1, "Select at least one goal")
})

type CampaignFormData = z.infer<typeof campaignSchema>

interface CreateCampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CreateCampaignModal = ({ isOpen, onClose }: CreateCampaignModalProps) => {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      platforms: [],
      content_types: [],
      campaign_goals: []
    }
  })

  const createCampaign = useMutation({
    mutationFn: async (data: CampaignFormData) => {
      const response = await axios.post('http://localhost:8000/api/v1/campaigns', data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['campaigns'])
      reset()
      onClose()
      // Navigate to the new campaign's details page
      router.push(`/campaigns/${data.id}`)
    },
    onError: (error) => {
      console.error('Failed to create campaign:', error)
      alert('Failed to create campaign. Please try again.')
    }
  })

  const onSubmit = (data: CampaignFormData) => {
    createCampaign.mutate(data)
  }

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      <div className="fixed inset-0 flex items-center justify-center p-4 overflow-y-auto">
        <Dialog.Panel className="mx-auto w-full max-w-2xl bg-white rounded-xl p-6 shadow-xl">
          <Dialog.Title className="text-2xl font-bold mb-6">Create New Campaign</Dialog.Title>
          
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Information */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name *</label>
                  <input
                    {...register("campaign_name")}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter campaign name"
                  />
                  {errors.campaign_name && <p className="text-red-500 text-sm mt-1">{errors.campaign_name.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand Name *</label>
                  <input
                    {...register("brand_name")}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter brand name"
                  />
                  {errors.brand_name && <p className="text-red-500 text-sm mt-1">{errors.brand_name.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                  <textarea
                    {...register("description")}
                    rows={3}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter campaign description"
                  />
                  {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>}
                </div>
              </div>

              {/* Campaign Details */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience *</label>
                  <input
                    {...register("target_audience")}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 18-24 year old fashion enthusiasts"
                  />
                  {errors.target_audience && <p className="text-red-500 text-sm mt-1">{errors.target_audience.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Budget Range *</label>
                  <input
                    {...register("budget_range")}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., $5,000 - $10,000"
                  />
                  {errors.budget_range && <p className="text-red-500 text-sm mt-1">{errors.budget_range.message}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Timeline *</label>
                  <input
                    {...register("timeline")}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 2 weeks"
                  />
                  {errors.timeline && <p className="text-red-500 text-sm mt-1">{errors.timeline.message}</p>}
                </div>
              </div>
            </div>

            {/* Platforms, Content Types, and Goals */}
            <div className="space-y-6 pt-4 border-t">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Platforms *</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {["Instagram", "YouTube", "TikTok", "Twitter", "Facebook"].map(platform => (
                    <label key={platform} className="inline-flex items-center bg-gray-50 p-3 rounded-lg hover:bg-gray-100">
                      <input
                        type="checkbox"
                        {...register("platforms")}
                        value={platform}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2">{platform}</span>
                    </label>
                  ))}
                </div>
                {errors.platforms && <p className="text-red-500 text-sm mt-1">{errors.platforms.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Content Types *</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {["Posts", "Stories", "Videos", "Reels", "Shorts", "Live"].map(type => (
                    <label key={type} className="inline-flex items-center bg-gray-50 p-3 rounded-lg hover:bg-gray-100">
                      <input
                        type="checkbox"
                        {...register("content_types")}
                        value={type}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2">{type}</span>
                    </label>
                  ))}
                </div>
                {errors.content_types && <p className="text-red-500 text-sm mt-1">{errors.content_types.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Goals *</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {[
                    "Brand Awareness",
                    "Product Promotion",
                    "Engagement",
                    "Sales",
                    "Lead Generation",
                    "Community Building"
                  ].map(goal => (
                    <label key={goal} className="inline-flex items-center bg-gray-50 p-3 rounded-lg hover:bg-gray-100">
                      <input
                        type="checkbox"
                        {...register("campaign_goals")}
                        value={goal.toLowerCase().replace(" ", "_")}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2">{goal}</span>
                    </label>
                  ))}
                </div>
                {errors.campaign_goals && <p className="text-red-500 text-sm mt-1">{errors.campaign_goals.message}</p>}
              </div>
            </div>

            {/* Form Actions */}
            <div className="mt-8 flex justify-end space-x-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Creating...' : 'Create Campaign'}
              </button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

export default CreateCampaignModal