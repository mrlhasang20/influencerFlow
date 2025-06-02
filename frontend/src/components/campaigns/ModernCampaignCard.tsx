import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface CampaignCardProps {
  id: string;
  name: string;
  brand: string;
  avatar: string;
  images?: string[];
  statValue?: number;
  badgeLabel?: string;
  category?: string;
  description?: string;
  onClick?: () => void;
}

export function ModernCampaignCard({
  id,
  name,
  brand,
  avatar,
  images = [],
  statValue = 234,
  badgeLabel = 'Badge',
  category = 'Collaborative project',
  description = 'Minim dolor in amet nulla laboris enim dolore consequat..',
  onClick,
}: CampaignCardProps) {
  return (
    <div 
      className="w-full max-w-[360px] flex flex-col bg-white rounded-[20px] shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
      onClick={onClick}
    >
      {/* Card Header */}
      <div className="p-6 flex flex-col justify-center items-start gap-2.5">
        <div className="w-full flex items-center gap-2.5">
          {/* Avatar and Info */}
          <div className="flex items-center gap-2.5 flex-grow">
            <div className="w-[60px] h-[60px] rounded-full overflow-hidden flex-shrink-0">
              <Image 
                src={avatar || '/placeholder-avatar.jpg'} 
                alt={name}
                width={60}
                height={60}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex flex-col justify-center gap-0.5">
              <h3 className="text-xl font-medium text-black">{name}</h3>
              <p className="text-sm text-green-500">{category}</p>
            </div>
          </div>
          
          {/* Three dots menu */}
          <div className="flex items-center justify-center">
            <button className="text-gray-700 hover:text-gray-900">
              <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-2">
        <h2 className="text-3xl font-bold mb-4">Collaborative work</h2>
        <h3 className="text-xl font-normal text-gray-500 mb-2">Introduction</h3>
        <p className="text-base text-black mb-6">{description}</p>

        {/* Collaborator Avatars */}
        <div className="flex items-center mb-6">
          {/* Display up to 4 avatars with +2 indicator if more */}
          <div className="flex -space-x-4">
            {[1, 2, 3, 4].map((_, index) => (
              <div 
                key={index} 
                className="w-10 h-10 rounded-full overflow-hidden border-2 border-white"
              >
                <Image 
                  src={`/placeholder-avatar-${index + 1}.jpg`} 
                  alt={`Collaborator ${index + 1}`}
                  width={40}
                  height={40}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
            <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center border-2 border-white">
              <span className="text-xs font-medium">+2</span>
            </div>
          </div>

          {/* Edit button */}
          <div className="ml-auto">
            <button className="w-10 h-10 bg-black rounded-full flex items-center justify-center text-white">
              <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
