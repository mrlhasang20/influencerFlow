import React from 'react';
import { FiUser, FiUserPlus, FiMapPin, FiActivity, FiShield, FiCheckCircle, FiX, FiMessageCircle, FiDollarSign, FiCloud, FiLayers, FiCalendar } from 'react-icons/fi';

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
  // Sample journey data - in a real implementation, this would come from an API
  const journeyData = {
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
    ],
  };

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
      <div className="min-w-[1200px] h-[800px] relative p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-6">Campaign Journey Map</h2>
        <p className="text-sm text-gray-600 mb-8">Visualizing the customer journey flow for campaign: <span className="font-medium">{campaignName}</span> (ID: {campaignId})</p>
        
        {/* Journey Map Grid */}
        <div className="relative">
          {/* First render the connections */}
          <svg className="absolute top-0 left-0 w-full h-full" style={{ zIndex: 0 }}>
            {journeyData.connections.map((connection, idx) => {
              const fromNode = journeyData.nodes.find(n => n.id === connection.from);
              const toNode = journeyData.nodes.find(n => n.id === connection.to);
              
              if (!fromNode || !toNode) return null;
              
              const startX = fromNode.position.x * 220 + 65;
              const startY = fromNode.position.y * 180 + 65;
              const endX = toNode.position.x * 220 + 65;
              const endY = toNode.position.y * 180 + 65;
              
              if (connection.type === 'vertical') {
                return (
                  <g key={idx}>
                    <line 
                      x1={startX} 
                      y1={startY + 65} 
                      x2={startX} 
                      y2={endY - 65} 
                      stroke="#C4C4C4" 
                      strokeWidth="2"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                    />
                    <circle cx={startX} cy={startY + 65} r="5" fill="white" stroke="#4680FF" strokeWidth="2" />
                    <polygon 
                      points={`${startX-6},${endY-65} ${startX+6},${endY-65} ${startX},${endY-55}`} 
                      fill="#C4C4C4" 
                    />
                  </g>
                );
              } else {
                // Horizontal connection
                const midY = connection.position === 'bottom' 
                  ? Math.max(startY + 100, endY + 100)
                  : (startY + endY) / 2;
                
                return (
                  <g key={idx}>
                    <line 
                      x1={startX} 
                      y1={startY} 
                      x2={startX} 
                      y2={midY} 
                      stroke="#C4C4C4" 
                      strokeWidth="2"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                    />
                    <line 
                      x1={startX} 
                      y1={midY} 
                      x2={endX} 
                      y2={midY} 
                      stroke="#C4C4C4" 
                      strokeWidth="2"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                    />
                    <line 
                      x1={endX} 
                      y1={midY} 
                      x2={endX} 
                      y2={endY} 
                      stroke="#C4C4C4" 
                      strokeWidth="2"
                      strokeDasharray={connection.dashed ? "5,5" : "none"}
                    />
                    <circle cx={startX} cy={startY} r="5" fill="white" stroke="#4680FF" strokeWidth="2" />
                    <polygon 
                      points={`${endX-6},${endY-10} ${endX+6},${endY-10} ${endX},${endY}`} 
                      fill="#C4C4C4" 
                    />
                  </g>
                );
              }
            })}
          </svg>

          {/* Then render the nodes */}
          {journeyData.nodes.map((node) => (
            <div 
              key={node.id}
              className={`absolute w-32 h-32 rounded-lg shadow-sm ${getCardBgColor(node.status)} transition-all duration-200 hover:shadow-md`}
              style={{
                left: `${node.position.x * 220}px`,
                top: `${node.position.y * 180}px`,
              }}
            >
              {/* Icon */}
              <div className="absolute top-2 left-1/2 transform -translate-x-1/2">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getIconBgColor(node.status)}`}>
                  {getIcon(node.icon)}
                </div>
              </div>
              
              {/* Title */}
              {node.type === 'decision' ? (
                <div className="absolute w-[90%] mx-auto left-0 right-0 bottom-4">
                  <div className={`py-1 px-2 rounded-full ${getButtonBgColor(node.status)} text-white text-xs font-medium text-center`}>
                    {node.title}
                  </div>
                </div>
              ) : (
                <div className="absolute w-full text-center bottom-4 px-2">
                  <p className={`text-xs font-medium ${getCardTextColor(node.status)}`}>{node.title}</p>
                </div>
              )}
              
              {/* Pain Points */}
              {node.painpoints && (
                <div className="absolute -top-2 -right-2">
                  <div className="bg-red-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm">
                    {Array.isArray(node.painpoints) && node.painpoints.length > 1 
                      ? `${node.painpoints[0]},${node.painpoints[1]}` 
                      : node.painpoints}
                  </div>
                </div>
              )}
              
              {/* Gain Points */}
              {node.gainpoints && (
                <div className="absolute -top-2 -right-2">
                  <div className="bg-green-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shadow-sm">
                    {Array.isArray(node.gainpoints) && node.gainpoints.length > 1 
                      ? `${node.gainpoints[0]},${node.gainpoints[1]}` 
                      : node.gainpoints}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

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
  );
};

export default JourneyMap;
