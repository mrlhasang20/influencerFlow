"use client";

import { CreateCampaignForm } from "@/components/campaigns/CreateCampaignForm";
import { Toaster } from "react-hot-toast";

export default function CreateCampaignPage() {
  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8">
            Create New Campaign
          </h1>
          <CreateCampaignForm />
        </div>
      </div>
      <Toaster position="top-right" />
    </main>
  );
}
