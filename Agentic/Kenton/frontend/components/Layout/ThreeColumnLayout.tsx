import React from 'react';

interface ThreeColumnLayoutProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
}

export function ThreeColumnLayout({ leftPanel, centerPanel, rightPanel }: ThreeColumnLayoutProps) {
  return (
    <div className="flex h-screen bg-[#0a0a0a] text-[#E5E5E5] overflow-hidden">
      {/* Left Panel - 30% */}
      <div className="w-[30%] min-w-[320px] max-w-[400px] border-r border-[#262626]">
        {leftPanel}
      </div>
      
      {/* Center Panel - 45% */}
      <div className="flex-1 min-w-[500px]">
        {centerPanel}
      </div>
      
      {/* Right Panel - 25% */}
      <div className="w-[25%] min-w-[300px] max-w-[380px] border-l border-[#262626]">
        {rightPanel}
      </div>
    </div>
  );
}