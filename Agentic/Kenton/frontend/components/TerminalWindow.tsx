'use client';

import React, { useRef, useEffect } from 'react';
import { Loader2, Terminal, CheckCircle2 } from 'lucide-react';

interface TerminalWindowProps {
  isThinking: boolean;
  content: string;
  status: string;
  isStreaming: boolean;
  isComplete: boolean;
}

const TerminalWindow: React.FC<TerminalWindowProps> = ({ 
  isThinking, 
  content, 
  status, 
  isStreaming,
  isComplete 
}) => {
  const terminalRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [content, status, isThinking]);

  return (
    <div className="bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      {/* Terminal Header */}
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="h-3 w-3 rounded-full bg-red-500"></div>
          <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
          <div className="h-3 w-3 rounded-full bg-green-500"></div>
        </div>
        <div className="text-gray-400 text-sm flex items-center">
          <Terminal className="w-4 h-4 mr-2" />
          <span>deepresearch-agent</span>
        </div>
        <div className="flex items-center space-x-2">
          {isStreaming && !isComplete && (
            <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
          )}
          {isComplete && (
            <CheckCircle2 className="w-4 h-4 text-green-400" />
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div 
        ref={terminalRef} 
        className="p-4 font-mono text-sm text-gray-300 bg-black bg-opacity-90 h-[600px] overflow-auto"
      >
        {/* Initial command */}
        <div className="mb-2">
          <span className="text-green-400">user@research-agent</span>
          <span className="text-white">:</span>
          <span className="text-blue-400">~</span>
          <span className="text-white">$ </span>
          <span className="text-yellow-200">run_research.py --query "{status.replace('🔬 Starting research on: ', '')}"</span>
        </div>

        {/* Status messages */}
        {status && status.includes('Initializing') && (
          <div className="text-gray-400 mb-2">[INFO] {status}</div>
        )}

        {/* Thinking animation */}
        {isThinking && (
          <div className="mb-4">
            <div className="text-cyan-400">[AGENT] Thinking...</div>
            <div className="flex items-center mt-1 text-cyan-200">
              <div className="typing-dots">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          </div>
        )}

        {/* Content area */}
        {content && (
          <div className="mt-4 text-green-100 whitespace-pre-wrap">
            <div className="text-yellow-400 mb-2">[OUTPUT] Final Research Report:</div>
            <div className="border border-gray-700 p-3 rounded bg-gray-900 overflow-auto max-h-[450px]">
              {/* The pre element preserves whitespace better for terminal-like display */}
              <pre className="text-green-100 font-mono whitespace-pre-wrap break-words">{content}</pre>
            </div>
            {isComplete && (
              <div className="mt-4 text-green-400">
                [SUCCESS] Research complete! ✅
              </div>
            )}
          </div>
        )}

        {/* Command prompt when complete */}
        {isComplete && (
          <div className="mt-4">
            <span className="text-green-400">user@research-agent</span>
            <span className="text-white">:</span>
            <span className="text-blue-400">~</span>
            <span className="text-white">$ </span>
            <span className="animate-pulse">▌</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TerminalWindow;