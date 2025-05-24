'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ThreeColumnLayout } from './Layout/ThreeColumnLayout';
import { MobileLayout } from './Layout/MobileLayout';
import { SuggestedPromptsPanel } from './LeftPanel/SuggestedPromptsPanel';
import { PromptInput } from './CenterPanel/PromptInput';
import { ResponseDisplay } from './CenterPanel/ResponseDisplay';
import { IntelligencePanel } from './RightPanel/IntelligencePanel';
import { LearnAIModule } from './LearnAI';
import { motion, AnimatePresence } from 'framer-motion';
import { GraduationCap, RotateCcw, Brain } from 'lucide-react';

interface EnhancedPrompt {
  original: string;
  enhanced: string;
  reason: string;
}

interface IntelligenceData {
  executionTime?: number;
  tokensUsed?: number;
  toolsCalled?: Array<{
    name: string;
    status: 'success' | 'failed';
    duration: number;
  }>;
  thinkingSteps?: string[];
  enhancedPrompts?: EnhancedPrompt[];
  modelsUsed?: Array<{
    name: string;
    purpose: string;
    tokensUsed?: number;
  }>;
}

export function EnhancedResearchApp() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [intelligenceData, setIntelligenceData] = useState<IntelligenceData>({});
  const [enhancedPrompts, setEnhancedPrompts] = useState<EnhancedPrompt[]>([]);
  const [showPromptLoadedAnimation, setShowPromptLoadedAnimation] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isMobile, setIsMobile] = useState(false);
  const [showLearnAI, setShowLearnAI] = useState(false);
  const [isDeepThink, setIsDeepThink] = useState(false);

  useEffect(() => {
    // Generate session ID
    setSessionId(`session-${Date.now()}`);
    
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handlePromptSelect = useCallback((selectedPrompt: string) => {
    setPrompt(selectedPrompt);
    setShowPromptLoadedAnimation(true);
    setTimeout(() => setShowPromptLoadedAnimation(false), 2000);
  }, []);

  const generateEnhancedPrompts = async (originalPrompt: string): Promise<EnhancedPrompt[]> => {
    try {
      // Call the backend to get AI-enhanced prompts
      const response = await fetch('/api/research/enhance-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: originalPrompt })
      });

      if (!response.ok) {
        throw new Error('Failed to enhance prompt');
      }

      const data = await response.json();
      return data.enhancements || [];
    } catch (error) {
      console.error('Error enhancing prompt:', error);
      // Fallback to basic enhancements if API fails
      return [
        {
          original: originalPrompt,
          enhanced: `${originalPrompt} Please provide specific data points, market statistics, and cite recent sources from 2024-2025.`,
          reason: "Added specificity for data and recency"
        }
      ];
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setResponse('');
    // Initialize with o3 model if Deep Think mode is active
    setIntelligenceData(isDeepThink ? {
      modelsUsed: [{
        name: 'o3-2025-04-16',
        purpose: 'Deep reasoning and analysis'
      }]
    } : {});

    // Start tracking metrics
    const startTime = Date.now();

    try {
      const res = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: prompt,
          sessionId,
          includeIntelligence: true,
          model: isDeepThink ? 'o3-2025-04-16' : 'gpt-4.1'
        }),
      });

      if (!res.ok) throw new Error('Research request failed');

      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let fullResponse = '';
      let intelligenceBuffer = '';
      let buffer = ''; // Buffer for incomplete lines

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n');
        
        // Keep the last line in buffer if it's incomplete
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() && line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log('SSE Event:', data.type, data); // Debug logging
              
              if (data.type === 'content') {
                fullResponse += data.content;
                setResponse(fullResponse);
              } else if (data.type === 'intelligence') {
                console.log('Intelligence data received:', data.content); // Debug logging
                intelligenceBuffer = data.content;
                // Update intelligence data immediately when received
                if (data.content) {
                  setIntelligenceData(prev => {
                    // Override models if Deep Think mode is active
                    let modelsUsed = data.content.modelsUsed || prev.modelsUsed;
                    if (isDeepThink && modelsUsed) {
                      // Replace any gpt-4.1 models with o3 when Deep Think is active
                      modelsUsed = modelsUsed.map((model: any) => {
                        if (model.name === 'gpt-4.1' || model.name === 'gpt-4.1-mini') {
                          return {
                            ...model,
                            name: 'o3-2025-04-16',
                            purpose: model.purpose || 'Deep reasoning and analysis'
                          };
                        }
                        return model;
                      });
                    } else if (isDeepThink && !modelsUsed) {
                      // If no models data yet, create o3 entry
                      modelsUsed = [{
                        name: 'o3-2025-04-16',
                        purpose: 'Deep reasoning and analysis',
                        tokensUsed: data.content.tokensUsed
                      }];
                    }
                    
                    const newData = {
                      ...prev,
                      executionTime: data.content.executionTime || prev.executionTime,
                      tokensUsed: data.content.tokensUsed || prev.tokensUsed,
                      toolsCalled: data.content.toolsCalled || prev.toolsCalled,
                      thinkingSteps: data.content.thinkingSteps || prev.thinkingSteps,
                      modelsUsed
                    };
                    console.log('Updated intelligence data:', newData); // Debug logging
                    return newData;
                  });
                }
              } else if (data.type === 'thinking') {
                console.log('Thinking step:', data.content); // Debug logging
                setIntelligenceData(prev => ({
                  ...prev,
                  thinkingSteps: [...(prev.thinkingSteps || []), data.content]
                }));
              } else if (data.type === 'tool') {
                console.log('Tool called:', data.tool); // Debug logging
                setIntelligenceData(prev => ({
                  ...prev,
                  toolsCalled: [...(prev.toolsCalled || []), data.tool]
                }));
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, 'Line:', line);
            }
          }
        }
      }

      // Generate enhanced prompts after response is complete
      const generatedEnhancements = await generateEnhancedPrompts(prompt);
      
      // Update with enhanced prompts (other data should already be set from streaming)
      setIntelligenceData(prev => ({
        ...prev,
        enhancedPrompts: generatedEnhancements
      }));

    } catch (error) {
      console.error('Research error:', error);
      setResponse('An error occurred while processing your request. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnhancePrompt = async () => {
    if (!prompt.trim()) return;
    
    try {
      setIsLoading(true);
      const newEnhancements = await generateEnhancedPrompts(prompt);
      setEnhancedPrompts(prev => [...newEnhancements, ...prev]);
      setIntelligenceData(prev => ({
        ...prev,
        enhancedPrompts: newEnhancements
      }));
      
      // Update the prompt to the first enhanced version
      if (newEnhancements.length > 0) {
        setPrompt(newEnhancements[0].enhanced);
        setShowPromptLoadedAnimation(true);
        setTimeout(() => setShowPromptLoadedAnimation(false), 2000);
      }
    } catch (error) {
      console.error('Error enhancing prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptEnhancement = (prompts?: EnhancedPrompt[]) => {
    if (prompts) {
      setEnhancedPrompts(prev => [...prompts, ...prev]);
    }
  };

  const handleReset = () => {
    setPrompt('');
    setResponse('');
    setIntelligenceData({});
    setEnhancedPrompts([]);
    setShowPromptLoadedAnimation(false);
    // Generate new session ID
    setSessionId(`session-${Date.now()}`);
  };

  const leftPanel = (
    <SuggestedPromptsPanel
      onPromptSelect={handlePromptSelect}
      currentPrompt={prompt}
      enhancedPrompts={enhancedPrompts}
    />
  );

  const centerPanel = (
    <div className="h-full flex flex-col bg-white">
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div>
            <motion.h1 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold text-gray-900 mb-2"
            >
              Kenton Deep Research
            </motion.h1>
            <p className="text-gray-500">Strategic intelligence for executive decision-making</p>
          </div>
          <div className="flex items-center gap-3">
            {response && (
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleReset}
                className="px-4 py-2 bg-red-50 text-red-600 rounded-lg flex items-center gap-2 hover:bg-red-100 transition-all duration-200 border border-red-200"
              >
                <RotateCcw className="w-5 h-5" />
                Reset
              </motion.button>
            )}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowLearnAI(true)}
              className="px-4 py-2 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-600 rounded-lg flex items-center gap-2 hover:from-blue-100 hover:to-purple-100 transition-all duration-200 border border-blue-200"
            >
              <GraduationCap className="w-5 h-5" />
              Learn AI
            </motion.button>
          </div>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col p-6 min-h-0">
        <div className="mb-6">
          <PromptInput
            value={prompt}
            onChange={setPrompt}
            onSubmit={handleSubmit}
            onEnhancePrompt={handleEnhancePrompt}
            isLoading={isLoading}
            showPromptLoadedAnimation={showPromptLoadedAnimation}
            isDeepThink={isDeepThink}
            onToggleDeepThink={() => setIsDeepThink(!isDeepThink)}
          />
        </div>
        
        <div className="flex-1 bg-gray-50 rounded-xl border border-gray-200 overflow-hidden min-h-0 shadow-sm">
          {response || isLoading ? (
            <div className="h-full flex flex-col">
              {isDeepThink && (
                <div className="px-4 py-2 bg-orange-50 border-b border-orange-200 flex items-center gap-2">
                  <Brain className="w-4 h-4 text-orange-600" />
                  <span className="text-sm text-orange-600 font-medium">Deep Think Mode Active (o3-2025-04-16)</span>
                </div>
              )}
              <div className="flex-1 min-h-0">
                <ResponseDisplay
                  content={response}
                  isStreaming={isLoading}
                  onEnhancePrompt={handleEnhancePrompt}
                  onFollowUp={(question) => {
                    setPrompt(question);
                    handleSubmit();
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">🧠</div>
                <p className="text-gray-600">Ready to explore strategic insights</p>
                <p className="text-sm text-gray-500 mt-2">Select a prompt from the left or type your own</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const rightPanel = (
    <IntelligencePanel
      data={intelligenceData}
      isStreaming={isLoading}
      onPromptEnhancement={handlePromptEnhancement}
    />
  );

  return (
    <>
      {isMobile ? (
        <MobileLayout
          leftPanel={leftPanel}
          centerPanel={centerPanel}
          rightPanel={rightPanel}
        />
      ) : (
        <ThreeColumnLayout
          leftPanel={leftPanel}
          centerPanel={centerPanel}
          rightPanel={rightPanel}
        />
      )}
      
      <AnimatePresence>
        {showLearnAI && (
          <LearnAIModule onClose={() => setShowLearnAI(false)} />
        )}
      </AnimatePresence>
    </>
  );
}