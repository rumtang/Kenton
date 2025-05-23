import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface SuggestedPrompt {
  category: string;
  icon: string;
  prompt: string;
  complexity: 'low' | 'medium' | 'high';
  tags: string[];
}

const suggestedPrompts: SuggestedPrompt[] = [
  {
    category: "Strategic Imperatives",
    icon: "🎯",
    prompt: "Deloitte Digital must proactively build its own fleet of agentic (AI-enabled, autonomous) solutions, rather than waiting for ecosystem partners like Salesforce to lead, or AI-first entrants like Anthropic",
    complexity: "high",
    tags: ["strategy", "competitive", "transformation"]
  },
  {
    category: "Learn AI",
    icon: "🎓",
    prompt: "How can I truly understand and harness AI? Give me a practical guide to embrace curiosity, build custom GPTs, assign roles, understand different models, experiment with tokens, and build something meaningful.",
    complexity: "medium",
    tags: ["learning", "AI fundamentals", "education"]
  },
  {
    category: "Market Intelligence",
    icon: "📊",
    prompt: "What are the latest developments in generative AI that could disrupt the consulting industry in the next 18 months?",
    complexity: "high",
    tags: ["AI", "disruption", "trends"]
  },
  {
    category: "Competitive Analysis",
    icon: "⚔️",
    prompt: "Compare Microsoft, Google, and Amazon's AI strategies and their implications for enterprise software markets",
    complexity: "high",
    tags: ["competitive", "tech giants", "analysis"]
  },
  {
    category: "Strategic Planning",
    icon: "🚀",
    prompt: "What emerging technologies should a $500M retail company invest in to remain competitive through 2030?",
    complexity: "medium",
    tags: ["planning", "retail", "investment"]
  },
  {
    category: "Market Analysis",
    icon: "📈",
    prompt: "Analyze the current state of the cybersecurity market and identify the top 3 investment opportunities",
    complexity: "high",
    tags: ["cybersecurity", "investment", "market"]
  },
  {
    category: "Industry Trends",
    icon: "🔮",
    prompt: "How will quantum computing impact financial services in the next 5 years?",
    complexity: "medium",
    tags: ["quantum", "fintech", "future"]
  },
  {
    category: "Quick Intel",
    icon: "⚡",
    prompt: "What's the current weather in Chicago and how might it impact logistics operations today?",
    complexity: "low",
    tags: ["operational", "real-time", "weather"]
  },
  {
    category: "Quick Intel",
    icon: "📰",
    prompt: "What are today's top technology news headlines?",
    complexity: "low",
    tags: ["news", "daily", "tech"]
  }
];

interface Props {
  onPromptSelect: (prompt: string) => void;
  currentPrompt: string;
  enhancedPrompts?: Array<{
    original: string;
    enhanced: string;
    reason: string;
  }>;
}

export function SuggestedPromptsPanel({ onPromptSelect, currentPrompt, enhancedPrompts = [] }: Props) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>('Strategic Imperatives');
  const [searchQuery, setSearchQuery] = useState('');

  const groupedPrompts = suggestedPrompts.reduce((acc, prompt) => {
    if (!acc[prompt.category]) acc[prompt.category] = [];
    acc[prompt.category].push(prompt);
    return acc;
  }, {} as Record<string, typeof suggestedPrompts>);

  const filteredGroupedPrompts = Object.entries(groupedPrompts).reduce((acc, [category, prompts]) => {
    const filtered = prompts.filter(p => 
      p.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );
    if (filtered.length > 0) acc[category] = filtered;
    return acc;
  }, {} as Record<string, typeof suggestedPrompts>);

  return (
    <div className="h-full bg-[#0a0a0a] overflow-y-auto">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-[#E5E5E5] mb-6">Explore Ideas</h2>
        
        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 bg-[#111111] border border-[#262626] rounded-lg text-[#E5E5E5] placeholder-[#666666] focus:border-[#0096FF] focus:outline-none transition-colors"
          />
        </div>

        {/* Enhanced Prompts Section */}
        {enhancedPrompts.length > 0 && (
          <div className="mb-8">
            <h3 className="text-sm font-medium text-[#A3A3A3] mb-3 flex items-center gap-2">
              <span className="text-yellow-500">✨</span> Enhanced Prompts
            </h3>
            <div className="space-y-3">
              {enhancedPrompts.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => onPromptSelect(item.enhanced)}
                  className="group w-full p-4 text-left rounded-lg bg-gradient-to-r from-[#111111] to-[#1a1a1a] border border-yellow-500/20 hover:border-yellow-500/40 transition-all duration-200"
                >
                  <p className="text-sm text-[#E5E5E5] leading-relaxed">{item.enhanced}</p>
                  <p className="text-xs text-[#666666] mt-2">Enhanced: {item.reason}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Suggested Prompts by Category */}
        {Object.entries(filteredGroupedPrompts).map(([category, categoryPrompts]) => (
          <div key={category} className="mb-6">
            <button
              onClick={() => setExpandedCategory(expandedCategory === category ? null : category)}
              className="flex items-center justify-between w-full text-left mb-3 group"
            >
              <h3 className="text-sm font-medium text-[#A3A3A3] group-hover:text-[#E5E5E5] transition-colors">
                {category}
              </h3>
              <ChevronDown
                className={`w-4 h-4 text-[#A3A3A3] transform transition-transform ${
                  expandedCategory === category ? 'rotate-180' : ''
                }`}
              />
            </button>
            
            <AnimatePresence>
              {expandedCategory === category && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="space-y-3 overflow-hidden"
                >
                  {categoryPrompts.map((item, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      onClick={() => onPromptSelect(item.prompt)}
                      className={`group w-full p-4 text-left rounded-lg transition-all duration-200 ${
                        currentPrompt === item.prompt
                          ? 'bg-[#0096FF]/10 border border-[#0096FF] shadow-lg shadow-[#0096FF]/20'
                          : 'bg-[#111111] border border-[#262626] hover:border-[#0096FF]/50 hover:bg-[#161616]'
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <span className="text-xl mt-0.5">{item.icon}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-[#E5E5E5] leading-relaxed break-words">
                            {item.prompt}
                          </p>
                          <div className="flex items-center gap-2 mt-2">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              item.complexity === 'high' ? 'bg-red-500/20 text-red-400' :
                              item.complexity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-green-500/20 text-green-400'
                            }`}>
                              {item.complexity}
                            </span>
                            {item.tags.map((tag, tagIdx) => (
                              <span key={tagIdx} className="text-xs text-[#666666]">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </div>
  );
}