import React from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface CreatorCardProps {
  id: string;
  name: string;
  role: string;
  avatar: string;
  badgeCount?: number;
  badgeLabel?: string;
  images?: string[];
  category?: string;
  description?: string;
}

export function CreatorCard({
  id,
  name,
  role,
  avatar,
  badgeCount,
  badgeLabel = 'Badge',
  images = [],
  category = 'Photographs',
  description = 'Minim dolor in amet nulla laboris enim dolore consequatt...',
}: CreatorCardProps) {
  return (
    <div className="w-full max-w-[360px] flex flex-col bg-white rounded-[20px] shadow-md overflow-hidden">
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
              <p className="text-sm text-gray-500">{role}</p>
            </div>
          </div>
          
          {/* SMALL Button */}
          <div className="flex justify-center items-center">
            <div className="px-4 py-2 border-2 border-black rounded-full">
              <span className="text-xs font-bold uppercase tracking-wider">SMALL</span>
            </div>
          </div>
        </div>
      </div>

      {/* Image Group */}
      {images && images.length > 0 && (
        <div className="flex flex-col justify-center items-center gap-1.5">
          {/* First row: 3 images */}
          <div className="flex justify-center items-center gap-1.5 w-full">
            {images.slice(0, 3).map((image, index) => (
              <div key={`top-${index}`} className="flex-1 h-[107.5px] bg-gray-100">
                <Image 
                  src={image} 
                  alt={`${name} portfolio ${index + 1}`}
                  width={120}
                  height={107.5}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
          </div>
          
          {/* Second row: 2 images */}
          {images.length > 3 && (
            <div className="flex justify-center items-center gap-1.5 w-full">
              {images.slice(3, 5).map((image, index) => (
                <div key={`bottom-${index}`} className="flex-1 h-[107.5px] bg-gray-100">
                  <Image 
                    src={image} 
                    alt={`${name} portfolio ${index + 4}`}
                    width={180}
                    height={107.5}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Card Stats */}
      <div className="flex justify-between items-center px-6 py-5 bg-gray-100">
        <div className="flex items-center gap-2.5">
          <div className="w-[31px] h-[31px] flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" className="w-6 h-6" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
            </svg>
          </div>
          <span className="text-xl font-black">{badgeCount || 234}</span>
        </div>
        
        <div className="flex justify-center items-center px-4 py-1.5 bg-black rounded">
          <span className="text-xs font-medium text-white">{badgeLabel}</span>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-6 flex flex-col justify-center items-start gap-2">
        <p className="text-base text-gray-500">{category}</p>
        <h2 className="text-2xl font-bold text-black">Lorem ipsum</h2>
        <p className="text-base text-black">{description}</p>
      </div>
    </div>
  );
}
