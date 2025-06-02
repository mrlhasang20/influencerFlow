'use client';
import Link from 'next/link';

interface Campaign {
  campaign_id: string;
  campaign_name: string;
  brand_name: string;
  status: string;
  created_at: string;
  description?: string;
}

interface CampaignCardProps {
  campaign: Campaign;
}

const CampaignCard = ({ campaign }: CampaignCardProps) => {
  // Add logging to debug the campaign data
  console.log('Campaign in card:', campaign);

  // Only render if we have a valid campaign_id
  if (!campaign?.campaign_id) {
    console.error('Campaign missing ID:', campaign);
    return null;
  }

  return (
    <Link 
      href={`/campaigns/${campaign.campaign_id}`}
      className="block bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
    >
      <div className="space-y-2">
        <h3 className="text-xl font-semibold text-gray-800">{campaign.campaign_name}</h3>
        <p className="text-gray-600">{campaign.brand_name}</p>
        {campaign.description && (
          <p className="text-gray-500 text-sm line-clamp-2">{campaign.description}</p>
        )}
        <div className="flex justify-between items-center pt-4">
          <span className={`px-3 py-1 rounded-full text-sm ${
            campaign.status === 'active' ? 'bg-green-100 text-green-800' :
            campaign.status === 'draft' ? 'bg-gray-100 text-gray-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {campaign.status}
          </span>
          <span className="text-sm text-gray-500">
            {new Date(campaign.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default CampaignCard;
