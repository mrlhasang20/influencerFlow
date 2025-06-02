interface Creator {
  creator_id: string;
  name: string;
  handle: string;
  platform: string;
  followers: number;
  engagement_rate: number;
  categories: string[];
  location?: string;
  content_style?: string;
  match_score?: number;
}

interface CreatorCardProps {
  creator: Creator;
}

export default function CreatorCard({ creator }: CreatorCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{creator.name}</h3>
          <p className="text-gray-600">@{creator.handle}</p>
        </div>
        <span className={`px-2 py-1 rounded text-sm ${
          creator.platform === 'Instagram' ? 'bg-pink-100 text-pink-800' :
          creator.platform === 'YouTube' ? 'bg-red-100 text-red-800' :
          creator.platform === 'TikTok' ? 'bg-purple-100 text-purple-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {creator.platform}
        </span>
      </div>
      
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Followers</span>
          <span className="font-medium">{creator.followers.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Engagement Rate</span>
          <span className="font-medium">{creator.engagement_rate.toFixed(2)}%</span>
        </div>
        {creator.location && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Location</span>
            <span className="font-medium">{creator.location}</span>
          </div>
        )}
      </div>

      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {creator.categories.map((category) => (
            <span
              key={`${creator.creator_id}-${category}`}
              className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs"
            >
              {category}
            </span>
          ))}
        </div>
      </div>

      {creator.match_score && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Match Score</span>
            <span className="text-sm font-medium text-blue-600">
              {Math.round(creator.match_score)}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
