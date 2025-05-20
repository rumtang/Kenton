'use client';

import { useState, useRef, useEffect } from 'react';
import { Loader2, Bot, AlertCircle, Terminal } from 'lucide-react';
import TerminalWindow from './TerminalWindow';

export default function SimpleResearch() {
  const [query, setQuery] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [content, setContent] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [debugLogs, setDebugLogs] = useState<string[]>([]);
  const outputRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [content, status]);

  const startResearch = async () => {
    if (!query.trim()) return;
    
    // Reset state
    setIsStreaming(true);
    setIsThinking(false);
    setIsComplete(false);
    setError(null);
    setContent('');
    setDebugLogs([]);
    setStatus('Initializing Deep Research Agent with gpt-4.1...');
    
    // Add initial status message
    setTimeout(() => {
      setStatus(`🔬 Starting research on: ${query}`);
    }, 500);

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, model: 'gpt-4.1' })
      });

      if (!response.ok) throw new Error('Failed to start research');
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error('No response body');
      
      let currentStatus = '';
      let hasStartedContent = false;
      
      // Show thinking state after a short delay
      const thinkingTimeout = setTimeout(() => {
        if (!hasStartedContent) {
          setIsThinking(true);
        }
      }, 2000);
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'status':
                  currentStatus = data.message || '';
                  setStatus(currentStatus);
                  break;
                  
                case 'thinking':
                  setIsThinking(true);
                  break;
                  
                case 'debug':
                  setDebugLogs(prev => [...prev, data.message || '']);
                  break;
                  
                case 'content':
                  // If we get content, we're no longer in thinking mode
                  clearTimeout(thinkingTimeout);
                  hasStartedContent = true;
                  setIsThinking(false);
                  
                  if (currentStatus) {
                    setStatus('');
                    currentStatus = '';
                  }
                  
                  setContent(prev => prev + (data.data || ''));
                  break;
                  
                case 'complete':
                  setIsStreaming(false);
                  setIsThinking(false);
                  setIsComplete(true);
                  setStatus('✅ Research complete!');
                  break;
                  
                case 'error':
                  setError(data.message || 'An error occurred');
                  setIsStreaming(false);
                  setIsThinking(false);
                  break;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start research');
      setIsStreaming(false);
      setIsThinking(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
      e.preventDefault();
      startResearch();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto p-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Deep Research Agent
          </h1>
          <p className="text-gray-600">
            AI-powered research with real-time analysis
          </p>
        </div>
        
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Enter your research question:
          </label>
          <div className="flex gap-4">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="What would you like to research?"
              className="flex-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={1}
              disabled={isStreaming}
            />
            
            <button
              onClick={startResearch}
              disabled={isStreaming || !query.trim()}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              {isStreaming ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Researching...
                </>
              ) : (
                <>
                  <Terminal className="w-4 h-4" />
                  Run Research
                </>
              )}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              {error}
            </p>
          </div>
        )}

        {/* Terminal Window */}
        {(isStreaming || content || status) && (
          <TerminalWindow 
            isThinking={isThinking}
            content={content}
            status={status || `🔬 Starting research on: ${query}`}
            isStreaming={isStreaming}
            isComplete={isComplete}
          />
        )}
        
        {/* Debug Logs - Hidden in production */}
        {debugLogs.length > 0 && process.env.NODE_ENV === 'development' && (
          <div className="mt-6 bg-gray-800 text-gray-300 p-4 rounded-lg overflow-auto max-h-40 text-xs font-mono">
            <div className="text-xs text-gray-500 mb-2">Debug Logs:</div>
            {debugLogs.map((log, i) => (
              <div key={i} className="mb-1">{log}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}