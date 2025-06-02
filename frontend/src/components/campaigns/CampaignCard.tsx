interface Campaign {
  campaign_id: string;
  brand_name: string;
  campaign_name: string;
  status: string;
  created_at: string;
  creators_discovered: number;
  next_steps: string[];
}

interface CampaignCardProps {
  campaign: Campaign;
}

export function CampaignCard({ campaign }: CampaignCardProps) {
  const statusColors = {
    created: "bg-green-100 text-green-800",
    draft: "bg-gray-100 text-gray-800",
    in_progress: "bg-blue-100 text-blue-800",
    completed: "bg-purple-100 text-purple-800",
    cancelled: "bg-red-100 text-red-800",
  };

  const statusColor =
    statusColors[campaign.status as keyof typeof statusColors] ||
    "bg-gray-100 text-gray-800";

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 truncate">
            {campaign.campaign_name}
          </h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${statusColor}`}
          >
            {campaign.status}
          </span>
        </div>
        <p className="mt-1 text-sm text-gray-500">{campaign.brand_name}</p>

        <div className="mt-4 space-y-2">
          <div className="flex items-center text-sm text-gray-500">
            <svg
              className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            {campaign.creators_discovered} creators discovered
          </div>

          <div className="flex flex-wrap gap-2">
            {campaign.next_steps.map((step, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
              >
                {step}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-500">
          Created {new Date(campaign.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
}
