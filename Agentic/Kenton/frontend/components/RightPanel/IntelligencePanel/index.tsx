import React, { useState } from 'react';
import { Brain, Zap, Wrench, Lightbulb, ChevronDown, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExecutionMetrics } from './ExecutionMetrics';
import { ThinkingProcess } from './ThinkingProcess';
import { ToolsUsage } from './ToolsUsage';
import { PromptSuggestions } from './PromptSuggestions';
import { ModelsUsage } from './ModelsUsage';

interface IntelligenceData {
  executionTime?: number;
  tokensUsed?: number;
  toolsCalled?: Array<{
    name: string;
    status: 'success' | 'failed';
    duration: number;
  }>;
  thinkingSteps?: string[];
  enhancedPrompts?: Array<{
    original: string;
    enhanced: string;
    reason: string;
  }>;
  modelsUsed?: Array<{
    name: string;
    purpose: string;
    tokensUsed?: number;
  }>;
}

interface Props {
  data: IntelligenceData;
  isStreaming?: boolean;
  onPromptEnhancement?: (prompts: IntelligenceData['enhancedPrompts']) => void;
}

export function IntelligencePanel({ data, isStreaming = false, onPromptEnhancement }: Props) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    execution: true,
    models: true,
    thinking: true,
    tools: true,
    suggestions: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="h-full bg-[#0a0a0a] overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-gradient-to-br from-[#0096FF]/20 to-purple-500/20 rounded-xl">
            <Brain className="w-6 h-6 text-[#0096FF]" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-[#E5E5E5]">Intelligence Panel</h2>
            <p className="text-xs text-[#666666]">The nerd stuff</p>
          </div>
        </div>

        {/* Execution Metrics */}
        <div className="mb-6">
          <button
            onClick={() => toggleSection('execution')}
            className="flex items-center justify-between w-full mb-3 group"
          >
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#0096FF]" />
              <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                Execution Metrics
              </h3>
            </div>
            <ChevronDown
              className={`w-4 h-4 text-[#666666] transform transition-transform ${
                expandedSections.execution ? 'rotate-180' : ''
              }`}
            />
          </button>
          
          <AnimatePresence>
            {expandedSections.execution && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ExecutionMetrics
                  executionTime={data.executionTime}
                  tokensUsed={data.tokensUsed}
                  isStreaming={isStreaming}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Models Used */}
        {data.modelsUsed && data.modelsUsed.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => toggleSection('models')}
              className="flex items-center justify-between w-full mb-3 group"
            >
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-[#0096FF]" />
                <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                  OpenAI Models Used
                </h3>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-[#666666] transform transition-transform ${
                  expandedSections.models ? 'rotate-180' : ''
                }`}
              />
            </button>
            
            <AnimatePresence>
              {expandedSections.models && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ModelsUsage models={data.modelsUsed} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Thinking Process */}
        {data.thinkingSteps && data.thinkingSteps.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => toggleSection('thinking')}
              className="flex items-center justify-between w-full mb-3 group"
            >
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-500" />
                <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                  Thinking Process
                </h3>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-[#666666] transform transition-transform ${
                  expandedSections.thinking ? 'rotate-180' : ''
                }`}
              />
            </button>
            
            <AnimatePresence>
              {expandedSections.thinking && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ThinkingProcess steps={data.thinkingSteps} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Tools Usage */}
        {data.toolsCalled && data.toolsCalled.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => toggleSection('tools')}
              className="flex items-center justify-between w-full mb-3 group"
            >
              <div className="flex items-center gap-2">
                <Wrench className="w-4 h-4 text-green-500" />
                <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                  Tools Used
                </h3>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-[#666666] transform transition-transform ${
                  expandedSections.tools ? 'rotate-180' : ''
                }`}
              />
            </button>
            
            <AnimatePresence>
              {expandedSections.tools && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ToolsUsage tools={data.toolsCalled} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Prompt Suggestions */}
        {data.enhancedPrompts && data.enhancedPrompts.length > 0 && (
          <div className="mb-6">
            <button
              onClick={() => toggleSection('suggestions')}
              className="flex items-center justify-between w-full mb-3 group"
            >
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-yellow-500" />
                <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                  Enhanced Prompts
                </h3>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-[#666666] transform transition-transform ${
                  expandedSections.suggestions ? 'rotate-180' : ''
                }`}
              />
            </button>
            
            <AnimatePresence>
              {expandedSections.suggestions && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <PromptSuggestions
                    suggestions={data.enhancedPrompts}
                    onApply={() => onPromptEnhancement?.(data.enhancedPrompts)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Live Streaming Indicator */}
        {isStreaming && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 p-4 bg-gradient-to-r from-[#0096FF]/10 to-purple-500/10 rounded-lg border border-[#0096FF]/20"
          >
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-2 h-2 bg-[#0096FF] rounded-full"
              />
              <span className="text-sm text-[#0096FF]">Processing your request...</span>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}