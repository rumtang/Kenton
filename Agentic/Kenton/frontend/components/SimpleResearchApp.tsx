'use client';

import { useState, useRef, useEffect } from 'react';
import { Maximize2, X, Clock, MessageSquare, Trash2 } from 'lucide-react';

export default function SimpleResearchApp() {
  const [query, setQuery] = useState('');
  const [model, setModel] = useState<'gpt-4.1' | 'o3'>('gpt-4.1');
  const [enableReasoning, setEnableReasoning] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [content, setContent] = useState('');
  const [reasoningTrace, setReasoningTrace] = useState('');
  const [showReasoning, setShowReasoning] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [showHistory, setShowHistory] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<any[]>([]);
  const [sessionSummary, setSessionSummary] = useState<any>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);

  // Generate or retrieve session ID on mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem('kenton_session_id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      loadSessionHistory(storedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(newSessionId);
      localStorage.setItem('kenton_session_id', newSessionId);
    }
  }, []);

  const loadSessionHistory = async (sid: string) => {
    try {
      const response = await fetch(`/api/session/${sid}/history`);
      if (response.ok) {
        const data = await response.json();
        setConversationHistory(data.history || []);
        setSessionSummary(data.summary);
      }
    } catch (err) {
      console.error('Failed to load session history:', err);
    }
  };

  const clearSession = async () => {
    if (!sessionId) return;
    
    if (confirm('Are you sure you want to clear the conversation history and start a new session?')) {
      try {
        await fetch(`/api/session/${sessionId}`, { method: 'DELETE' });
        
        // Generate new session ID
        const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        localStorage.setItem('kenton_session_id', newSessionId);
        
        // Clear UI
        setConversationHistory([]);
        setSessionSummary(null);
        setContent('');
        setReasoningTrace('');
        setQuery('');
        setError(null);
        setStatus('New session started');
        
        setTimeout(() => setStatus(''), 3000);
      } catch (err) {
        console.error('Failed to clear session:', err);
        setError('Failed to clear session');
      }
    }
  };

  const startResearch = async () => {
    if (!query.trim()) return;
    
    setIsStreaming(true);
    setError(null);
    setContent('');
    setReasoningTrace('');
    setShowReasoning(false);
    setStatus('Initializing...');

    try {
      const response = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          model, 
          enable_reasoning: enableReasoning,
          sessionId 
        })
      });

      if (!response.ok) throw new Error('Failed to start research');
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error('No response body');
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last line in buffer if it's incomplete
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.trim() && line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              switch (data.type) {
                case 'status':
                  setStatus(data.message);
                  break;
                  
                case 'content':
                  setStatus('');
                  setContent(prev => prev + data.content);
                  break;
                  
                case 'reasoning_start':
                  setStatus('Processing reasoning...');
                  break;
                  
                case 'reasoning':
                  setReasoningTrace(prev => prev + data.data);
                  break;
                  
                case 'reasoning_end':
                  setStatus('Reasoning complete, generating response...');
                  break;
                  
                case 'done':
                  setIsStreaming(false);
                  setStatus('Research complete');
                  // Reload history after completion
                  setTimeout(() => loadSessionHistory(sessionId), 1000);
                  break;
                  
                case 'error':
                  setError(data.error || data.message);
                  setIsStreaming(false);
                  break;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e, 'Line:', line);
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start research');
      setIsStreaming(false);
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Simple Research Interface</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 flex items-center gap-2"
              title="View conversation history"
            >
              <MessageSquare size={20} />
              History
            </button>
            <button
              onClick={clearSession}
              className="px-4 py-2 bg-red-100 text-red-700 rounded hover:bg-red-200 flex items-center gap-2"
              title="Clear history and start new session"
            >
              <Trash2 size={20} />
              New Session
            </button>
          </div>
        </div>
        
        {/* Session Info */}
        {sessionSummary && sessionSummary.total_exchanges > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
            <div className="flex items-center gap-2 text-sm text-blue-700">
              <Clock size={16} />
              <span>Session: {sessionSummary.total_exchanges} exchanges, {sessionSummary.duration_minutes} minutes</span>
            </div>
          </div>
        )}
        
        {/* History Panel */}
        {showHistory && conversationHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6 max-h-96 overflow-y-auto">
            <h2 className="font-bold mb-4">Conversation History</h2>
            <div className="space-y-4">
              {conversationHistory.map((entry, idx) => (
                <div key={idx} className="border-l-2 border-gray-200 pl-4">
                  <div className="text-xs text-gray-500 mb-1">{formatTimestamp(entry.timestamp)}</div>
                  <div className="mb-2">
                    <span className="font-medium text-blue-600">Q:</span> {entry.query}
                  </div>
                  <div className="text-sm text-gray-700">
                    <span className="font-medium text-green-600">A:</span> {entry.response.substring(0, 200)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research question..."
            className="w-full p-3 border rounded mb-4"
            rows={3}
            disabled={isStreaming}
          />
          
          <div className="flex gap-4 items-center">
            <select
              value={model}
              onChange={(e) => setModel(e.target.value as 'gpt-4.1' | 'o3')}
              className="p-2 border rounded"
              disabled={isStreaming}
            >
              <option value="gpt-4.1">GPT-4.1</option>
              <option value="o3">O3</option>
            </select>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enable-reasoning"
                checked={enableReasoning}
                onChange={(e) => setEnableReasoning(e.target.checked)}
                disabled={isStreaming}
                className="w-4 h-4"
              />
              <label htmlFor="enable-reasoning" className="text-sm">
                Enable reasoning
              </label>
            </div>
            
            <button
              onClick={startResearch}
              disabled={isStreaming || !query.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isStreaming ? 'Researching...' : 'Start Research'}
            </button>
          </div>
          
          {sessionId && (
            <div className="mt-4 text-xs text-gray-500">
              Session ID: {sessionId}
            </div>
          )}
        </div>
        
        {status && (
          <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
            {status}
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-4 mb-4">
            Error: {error}
          </div>
        )}
        
        {(content || reasoningTrace) && (
          <>
            {/* Overlay */}
            {isExpanded && (
              <div 
                className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300"
                onClick={() => setIsExpanded(false)}
              />
            )}
            
            {/* Research Output Panel */}
            <div 
              className={`
                ${isExpanded 
                  ? 'fixed inset-8 z-50 shadow-2xl overflow-auto' 
                  : 'relative'
                } 
                bg-white rounded-lg shadow p-6 transition-all duration-300
              `}
            >
              {reasoningTrace && (
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <h2 className="font-bold">Reasoning Process</h2>
                    <button 
                      onClick={() => setShowReasoning(!showReasoning)}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      {showReasoning ? 'Hide Reasoning' : 'Show Reasoning'}
                    </button>
                  </div>
                  
                  {showReasoning && (
                    <div className="bg-gray-50 p-4 rounded border border-gray-200">
                      <pre className="whitespace-pre-wrap font-mono text-xs text-gray-700">
                        {reasoningTrace}
                      </pre>
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-bold">Research Output</h2>
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                  aria-label={isExpanded ? 'Collapse' : 'Expand'}
                >
                  {isExpanded ? <X size={20} /> : <Maximize2 size={20} />}
                </button>
              </div>
              
              <pre className="whitespace-pre-wrap font-mono text-sm">
                {content}
              </pre>
            </div>
          </>
        )}
      </div>
    </div>
  );
}