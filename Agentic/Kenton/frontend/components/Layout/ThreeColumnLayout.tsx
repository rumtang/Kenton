import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface ThreeColumnLayoutProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
}

export function ThreeColumnLayout({ leftPanel, centerPanel, rightPanel }: ThreeColumnLayoutProps) {
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 overflow-hidden">
      {/* Left Panel - Collapsible */}
      <div className={`relative transition-all duration-300 ease-in-out bg-white border-r border-gray-200 ${
        isLeftPanelCollapsed ? 'w-0 min-w-0' : 'w-[25%] min-w-[280px] max-w-[350px]'
      }`}>
        <div className={`${isLeftPanelCollapsed ? 'invisible' : 'visible'} h-full`}>
          {leftPanel}
        </div>
        
        {/* Toggle Button */}
        <button
          onClick={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
          className={`absolute top-1/2 -translate-y-1/2 z-10 w-6 h-12 bg-white border border-gray-200 rounded-r-md hover:bg-gray-50 flex items-center justify-center transition-all duration-300 ${
            isLeftPanelCollapsed ? 'left-0 border-l-0' : '-right-6'
          }`}
          aria-label={isLeftPanelCollapsed ? 'Expand left panel' : 'Collapse left panel'}
        >
          {isLeftPanelCollapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          )}
        </button>
      </div>
      
      {/* Center Panel - Expands when left panel is collapsed */}
      <div className="flex-1 min-w-[500px] bg-white">
        {centerPanel}
      </div>
      
      {/* Right Panel - 25% */}
      <div className="w-[25%] min-w-[300px] max-w-[380px] bg-white border-l border-gray-200">
        {rightPanel}
      </div>
    </div>
  );
}