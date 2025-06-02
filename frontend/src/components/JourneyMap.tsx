import React, { useEffect, useState } from 'react';
import { FiUser, FiUserPlus, FiMapPin, FiActivity, FiShield, FiCheckCircle, FiX, FiMessageCircle, FiDollarSign, FiCloud, FiLayers, FiCalendar, FiArrowLeft } from 'react-icons/fi';

interface JourneyMapProps {
  campaignId: string;
  campaignName: string;
}

interface Connection {
  from: string;
  to: string;
  type: string;
  position?: string;
  dashed?: boolean;
}

const JourneyMap: React.FC<JourneyMapProps> = ({ campaignId, campaignName }) => {
  // Define types for journey data
  interface JourneyNode {
    id: string;
    type: string;
    title: string;
    icon: string;
    status: string;
    position: { x: number; y: number };
    painpoints?: number[];
    gainpoints?: number[];
  }

  interface JourneyData {
    nodes: JourneyNode[];
    connections: Connection[];
  }

  // State to store journey data
  const [journeyData, setJourneyData] = useState<JourneyData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Mock API fetch function - in a real app, this would be a real API call
  useEffect(() => {
    const fetchJourneyData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Simulate API call with timeout
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Generate different journey maps based on campaign ID
        // In a real app, this would be fetched from an API
        const data = generateJourneyDataForCampaign(campaignId);
        setJourneyData(data);
      } catch (err) {
        setError('Failed to load journey map data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchJourneyData();
  }, [campaignId]);
  
  // Generate different journey data based on campaign ID
  const generateJourneyDataForCampaign = (campaignId: string): JourneyData => {
    // Base structure that's common to all journey maps
    const baseStructure = {
    nodes: [
      {
        id: 'user',
        type: 'decision',
        title: 'User',
        icon: 'user',
        status: 'primary',
        position: { x: 0, y: 0 },
      },
      {
        id: 'new_user',
        type: 'decision',
        title: 'New User',
        icon: 'user-plus',
        status: 'primary',
        position: { x: 1, y: 0 },
      },
      {
        id: 'user_location',
        type: 'process',
        title: 'User Location Verified',
        icon: 'map-pin',
        status: 'default',
        position: { x: 2, y: 0 },
        painpoints: [2, 3],
      },
      {
        id: 'user_security',
        type: 'process',
        title: 'User Security',
        icon: 'identity',
        status: 'default',
        position: { x: 2, y: 1 },
        gainpoints: [4],
      },
      {
        id: 'user_verified',
        type: 'process',
        title: 'User Verified',
        icon: 'shield',
        status: 'default',
        position: { x: 3, y: 1 },
      },
      {
        id: 'booked_appointment',
        type: 'process',
        title: 'Booked Appointment',
        icon: 'calendar',
        status: 'default',
        position: { x: 0, y: 2 },
        painpoints: [1],
      },
      {
        id: 'user_onboarding',
        type: 'process',
        title: 'New User Onboarding',
        icon: 'layers',
        status: 'default',
        position: { x: 1, y: 2 },
        gainpoints: [2, 3],
      },
      {
        id: 'failed_auth',
        type: 'process',
        title: 'Failed User Auth',
        icon: 'x',
        status: 'failed',
        position: { x: 2, y: 2 },
      },
      {
        id: 'send_message',
        type: 'process',
        title: 'Send Message New User',
        icon: 'message-circle',
        status: 'default',
        position: { x: 2, y: 3 },
      },
      {
        id: 'title',
        type: 'process',
        title: 'Title (Sub-title Possible)',
        icon: 'dollar-sign',
        status: 'default',
        position: { x: 3, y: 3 },
        painpoints: [4],
      },
      {
        id: 'failed_title',
        type: 'process',
        title: 'Title (Sub-title Possible)',
        icon: 'x',
        status: 'failed',
        position: { x: 4, y: 3 },
      },
      {
        id: 'cloud_title',
        type: 'decision',
        title: 'Title (Sub-title Possible)',
        icon: 'cloud',
        status: 'default',
        position: { x: 3, y: 4 },
      },
      {
        id: 'item_fulfilled',
        type: 'decision',
        title: 'Item Fulfilled',
        icon: 'check-circle',
        status: 'success',
        position: { x: 4, y: 4 },
        gainpoints: [5],
      },
    ],
    // Define connections between nodes
    connections: [
      { from: 'user', to: 'booked_appointment', type: 'vertical', dashed: false },
      { from: 'new_user', to: 'user_onboarding', type: 'vertical', dashed: false },
      { from: 'user_location', to: 'user_security', type: 'vertical', dashed: false },
      { from: 'user_security', to: 'failed_auth', type: 'vertical', dashed: false },
      { from: 'failed_auth', to: 'send_message', type: 'vertical', dashed: false },
      { from: 'user_onboarding', to: 'send_message', type: 'horizontal', position: 'bottom', dashed: true },
      { from: 'send_message', to: 'title', type: 'horizontal', dashed: false },
      { from: 'title', to: 'failed_title', type: 'horizontal', dashed: true },
      { from: 'title', to: 'cloud_title', type: 'vertical', dashed: false },
      { from: 'cloud_title', to: 'item_fulfilled', type: 'horizontal', dashed: false },
      // Add horizontal connection between user and new_user
      { from: 'user', to: 'new_user', type: 'horizontal', dashed: false },
      // Add horizontal connection between new_user and user_location
      { from: 'new_user', to: 'user_location', type: 'horizontal', dashed: false },
      // Add horizontal connection between user_verified and title
      { from: 'user_verified', to: 'title', type: 'horizontal', position: 'bottom', dashed: true },
    ],
  };

  // Define different journey maps based on campaign ID
  switch(campaignId) {
    case 'camp-001': // Summer Collection Launch
      return baseStructure; // Use the base structure for this campaign
      
    case 'camp-002': // Holiday Season Promotion
      return {
        nodes: [
          ...baseStructure.nodes.filter(n => n.id !== 'failed_auth' && n.id !== 'failed_title'),
          {
            id: 'holiday_special',
            type: 'decision',
            title: 'Holiday Special Offer',
            icon: 'dollar-sign',
            status: 'primary',
            position: { x: 0, y: 3 },
            gainpoints: [1, 5],
          }
        ],
        connections: [
          ...baseStructure.connections.filter(c => 
            c.from !== 'failed_auth' && c.to !== 'failed_auth' && 
            c.from !== 'failed_title' && c.to !== 'failed_title'
          ),
          { from: 'booked_appointment', to: 'holiday_special', type: 'vertical', dashed: false },
          { from: 'holiday_special', to: 'send_message', type: 'horizontal', dashed: false },
        ]
      };
      
    case 'camp-003': // Back to School Campaign
      return {
        nodes: [
          ...baseStructure.nodes,
          {
            id: 'school_special',
            type: 'process',
            title: 'School Campaign',
            icon: 'calendar',
            status: 'primary',
            position: { x: 5, y: 2 },
            gainpoints: [3],
          }
        ],
        connections: [
          ...baseStructure.connections,
          { from: 'item_fulfilled', to: 'school_special', type: 'horizontal', dashed: true },
        ]
      };
      
    case 'camp-004': // Product Awareness Drive
      // Simplified journey for awareness campaign
      return {
        nodes: baseStructure.nodes.filter(n => 
          ['user', 'new_user', 'user_onboarding', 'send_message', 'title', 'cloud_title'].includes(n.id)
        ),
        connections: baseStructure.connections.filter(c => 
          ['user', 'new_user', 'user_onboarding', 'send_message', 'title', 'cloud_title'].includes(c.from) && 
          ['user', 'new_user', 'user_onboarding', 'send_message', 'title', 'cloud_title'].includes(c.to)
        )
      };
      
    case 'camp-005': // Brand Loyalty Program
      // Complex journey with more connections for loyalty program
      return {
        nodes: [
          ...baseStructure.nodes,
          {
            id: 'loyalty_reward',
            type: 'decision',
            title: 'Loyalty Reward',
            icon: 'dollar-sign',
            status: 'success',
            position: { x: 5, y: 4 },
            gainpoints: [2, 3, 4],
          }
        ],
        connections: [
          ...baseStructure.connections,
          { from: 'item_fulfilled', to: 'loyalty_reward', type: 'horizontal', dashed: false },
        ]
      };
      
    case 'camp-006': // New Market Expansion
      // Journey focused on new markets
      return {
        nodes: [
          ...baseStructure.nodes.filter(n => !['failed_auth', 'failed_title'].includes(n.id)),
          {
            id: 'market_entry',
            type: 'process',
            title: 'Market Entry Point',
            icon: 'map-pin',
            status: 'primary',
            position: { x: 5, y: 0 },
          },
          {
            id: 'localization',
            type: 'process',
            title: 'Localization',
            icon: 'layers',
            status: 'default',
            position: { x: 5, y: 1 },
            gainpoints: [1, 2],
          }
        ],
        connections: [
          ...baseStructure.connections.filter(c => 
            !['failed_auth', 'failed_title'].includes(c.from) && 
            !['failed_auth', 'failed_title'].includes(c.to)
          ),
          { from: 'user_location', to: 'market_entry', type: 'horizontal', dashed: false },
          { from: 'market_entry', to: 'localization', type: 'vertical', dashed: false },
          { from: 'localization', to: 'item_fulfilled', type: 'horizontal', position: 'bottom', dashed: true },
        ]
      };
      
    default:
      return baseStructure;
  }
};

  // If data is loading or there's an error, show appropriate message
  if (isLoading) {
    return (
      <div className="w-full min-h-[400px] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="h-8 w-64 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 w-48 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 w-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="w-full min-h-[400px] flex items-center justify-center">
        <div className="text-red-500 text-center">
          <p className="text-lg font-medium mb-2">Error loading journey map</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }
  
  if (!journeyData) {
    return null;
  }

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'user': return <FiUser className="h-5 w-5" />;
      case 'user-plus': return <FiUserPlus className="h-5 w-5" />;
      case 'map-pin': return <FiMapPin className="h-5 w-5" />;
      case 'identity': return <FiActivity className="h-5 w-5" />;
      case 'shield': return <FiShield className="h-5 w-5" />;
      case 'check-circle': return <FiCheckCircle className="h-5 w-5" />;
      case 'x': return <FiX className="h-5 w-5" />;
      case 'message-circle': return <FiMessageCircle className="h-5 w-5" />;
      case 'dollar-sign': return <FiDollarSign className="h-5 w-5" />;
      case 'cloud': return <FiCloud className="h-5 w-5" />;
      case 'layers': return <FiLayers className="h-5 w-5" />;
      case 'calendar': return <FiCalendar className="h-5 w-5" />;
      default: return <FiUser className="h-5 w-5" />;
    }
  };

  const getCardBgColor = (status: string) => {
    switch (status) {
      case 'primary': return 'bg-blue-100';
      case 'success': return 'bg-green-100';
      case 'failed': return 'bg-red-100';
      default: return 'bg-gray-50';
    }
  };

  const getCardTextColor = (status: string) => {
    switch (status) {
      case 'primary': return 'text-blue-800';
      case 'success': return 'text-green-800';
      case 'failed': return 'text-red-800';
      default: return 'text-gray-800';
    }
  };

  const getIconBgColor = (status: string) => {
    switch (status) {
      case 'primary': return 'bg-blue-500 text-white';
      case 'success': return 'bg-green-500 text-white';
      case 'failed': return 'bg-red-500 text-white';
      default: return 'bg-white text-blue-500';
    }
  };

  const getButtonBgColor = (status: string) => {
    switch (status) {
      case 'primary': return 'bg-blue-500';
      case 'success': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-blue-500';
    }
  };

  return (
    <div className="w-full overflow-auto py-8">
      <div className="min-w-[1200px] h-[800px] relative p-6 bg-grid-pattern rounded-lg" 
           style={{ 
             backgroundImage: 'radial-gradient(rgba(210, 210, 210, 0.4) 1px, transparent 0)',
             backgroundSize: '30px 30px',
             backgroundPosition: '15px 15px',
           }}>
        {/* Back button */}
        <button 
          onClick={() => window.history.back()} 
          className="absolute top-4 left-4 flex items-center text-indigo-600 hover:text-indigo-800 transition-colors duration-200"
        >
          <FiArrowLeft className="mr-1" />
          <span className="text-sm font-medium">Back to Campaigns</span>
        </button>
        
        <h2 className="text-xl font-semibold text-gray-800 mb-6 pl-24">Campaign Journey Map</h2>
        <p className="text-sm text-gray-600 mb-8 pl-24">Visualizing the customer journey flow for campaign: <span className="font-medium">{campaignName}</span> (ID: {campaignId})</p>
        
        {/* Journey Map Grid */}
        <div className="relative" style={{ marginTop: '30px' }}>
          {/* First render the connections */}
          <svg className="absolute top-0 left-0 w-full h-full" style={{ zIndex: 0, pointerEvents: 'none' }}>
            {journeyData && journeyData.connections && journeyData.connections.map((connection: Connection, idx: number) => {
              const fromNode = journeyData.nodes.find((n: JourneyNode) => n.id === connection.from);
              const toNode = journeyData.nodes.find((n: JourneyNode) => n.id === connection.to);
              
              if (!fromNode || !toNode) return null;
                            // Calculate node centers for connection points
                const startX = fromNode.position.x * 220 + 64; // Center of node
                const startY = fromNode.position.y * 180 + 64; // Center of node
                const endX = toNode.position.x * 220 + 64; // Center of node
                const endY = toNode.position.y * 180 + 64; // Center of node
              
              if (connection.type === 'vertical') {
                // For vertical connections (nodes stacked vertically)
                return (
                  <g key={`connection-${idx}`}>
                    <line 
                      x1={startX} 
                      y1={startY + 16} // Offset from center toward bottom of node
                      x2={startX} 
                      y2={endY - 16} // Offset from center toward top of node
                      stroke="#6366F1" 
                      strokeWidth="3"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                      strokeOpacity="0.9"
                    />
                    <circle cx={startX} cy={startY + 16} r="4" fill="white" stroke="#4F46E5" strokeWidth="2" />
                    <polygon 
                      points={`${startX-6},${endY-22} ${startX+6},${endY-22} ${startX},${endY-16}`} 
                      fill="#6366F1" 
                    />
                  </g>
                );
              } else {
                // Horizontal or angled connection (nodes side by side)
                const midY = connection.position === 'bottom' 
                  ? Math.max(startY + 70, endY + 70) // Further down for bottom position
                  : (startY + endY) / 2; // Middle point for default position
                
                return (
                  <g key={`connection-${idx}`}>
                    {/* Vertical line from start node down */}
                    <line 
                      x1={startX} 
                      y1={startY + 16} // Start from bottom edge of node
                      x2={startX} 
                      y2={midY} 
                      stroke="#6366F1" 
                      strokeWidth="3"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                      strokeOpacity="0.9"
                    />
                    {/* Horizontal line connecting vertical segments */}
                    <line 
                      x1={startX} 
                      y1={midY} 
                      x2={endX} 
                      y2={midY} 
                      stroke="#6366F1" 
                      strokeWidth="3"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                      strokeOpacity="0.9"
                    />
                    {/* Vertical line up to end node */}
                    <line 
                      x1={endX} 
                      y1={midY} 
                      x2={endX} 
                      y2={endY - 16} // End at top edge of node
                      stroke="#6366F1" 
                      strokeWidth="3"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                      strokeOpacity="0.9"
                    />
                    {/* Start circle */}
                    <circle cx={startX} cy={startY + 16} r="4" fill="white" stroke="#4F46E5" strokeWidth="2" />
                    {/* End arrow */}
                    <polygon 
                      points={`${endX-6},${endY-22} ${endX+6},${endY-22} ${endX},${endY-16}`} 
                      fill="#6366F1" 
                    />
                  </g>
                );
              }
            })}
          </svg>

          {/* Then render the nodes */}
          {journeyData.nodes.map((node: JourneyNode) => {
            const { id, type, title, icon, status, position, painpoints = [], gainpoints = [] } = node;
            return (
              <div 
                key={id}
                className={`absolute w-32 h-32 rounded-lg shadow-sm ${getCardBgColor(status)} transition-all duration-200 hover:shadow-md`}
                style={{
                  left: `${position.x * 220}px`,
                  top: `${position.y * 180}px`,
                }}
              >
                {/* Icon */}
                <div className="absolute top-2 left-1/2 transform -translate-x-1/2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getIconBgColor(status)}`}>
                    {getIcon(icon)}
                  </div>
                </div>
                
                {/* Title */}
                {type === 'decision' ? (
                  <div className="absolute w-[90%] mx-auto left-0 right-0 bottom-4">
                    <div className={`py-1 px-2 rounded-full ${getButtonBgColor(status)} text-white text-xs font-medium text-center`}>
                      {title}
                    </div>
                  </div>
                ) : (
                  <div className="absolute w-full text-center bottom-4 px-2">
                    <p className={`text-xs font-medium ${getCardTextColor(status)}`}>{title}</p>
                  </div>
                )}
                
                {/* Pain Points */}
                {painpoints && painpoints.length > 0 && (
                  <div className="absolute -top-2 -right-2">
                    <div className="bg-red-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm">
                      {painpoints.length > 1 
                        ? `${painpoints[0]},${painpoints[1]}` 
                        : painpoints[0]
                      }
                    </div>
                  </div>
                )}

                {/* Gain Points */}
                {gainpoints && gainpoints.length > 0 && (
                  <div className="absolute -top-2 -left-2">
                    <div className="bg-green-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm">
                      {gainpoints.length > 1 
                        ? `${gainpoints[0]},${gainpoints[1]}` 
                        : gainpoints[0]
                      }
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          
          {/* Legend */}
          <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-sm border border-gray-100 flex flex-col space-y-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-blue-100"></div>
              <span className="text-xs text-gray-700">Decision Point</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-gray-50"></div>
              <span className="text-xs text-gray-700">Process Point</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-100"></div>
              <span className="text-xs text-gray-700">Failed Point</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-100"></div>
              <span className="text-xs text-gray-700">Success Point</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-xs text-gray-700">Pain Point</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-xs text-gray-700">Gain Point</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { JourneyMap as default };
