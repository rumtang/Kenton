import React, { useRef, useEffect, useState } from 'react';
import { Send, X, Sparkles, Wand2, Brain } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onEnhancePrompt: () => void;
  isLoading?: boolean;
  showPromptLoadedAnimation?: boolean;
  isDeepThink?: boolean;
  onToggleDeepThink?: () => void;
}

export function PromptInput({ value, onChange, onSubmit, onEnhancePrompt, isLoading = false, showPromptLoadedAnimation = false, isDeepThink = false, onToggleDeepThink }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const charLimit = 2000;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="relative">
      <AnimatePresence>
        {showPromptLoadedAnimation && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-[#0096FF] text-white px-3 py-1 rounded-full text-sm flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            Prompt loaded!
          </motion.div>
        )}
      </AnimatePresence>

      <div className={`relative bg-white rounded-xl border-2 transition-all duration-200 ${
        isFocused ? 'border-blue-500 shadow-lg shadow-blue-500/10' : 'border-gray-200'
      }`}>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Explore something..."
          className="w-full px-6 py-4 bg-transparent text-gray-900 placeholder-gray-400 resize-none focus:outline-none"
          style={{ minHeight: '60px' }}
          disabled={isLoading}
        />
        
        <div className="flex items-center justify-between px-6 py-3 border-t border-gray-100">
          <div className="flex items-center gap-4">
            <span className={`text-xs ${value.length > charLimit * 0.9 ? 'text-red-500' : 'text-gray-500'}`}>
              {value.length} / {charLimit}
            </span>
            <span className="text-xs text-gray-500">
              {typeof window !== 'undefined' && navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'} + Enter to submit
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {value && (
              <button
                onClick={() => onChange('')}
                className="p-2 text-gray-400 hover:text-gray-700 transition-colors"
                disabled={isLoading}
              >
                <X className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onEnhancePrompt}
              disabled={!value.trim() || isLoading}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 mr-2 ${
                !value.trim() || isLoading
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700 shadow-md'
              }`}
              title="Enhance this prompt"
            >
              <Wand2 className="w-4 h-4" />
              Enhance
            </button>
            {onToggleDeepThink && (
              <button
                onClick={onToggleDeepThink}
                disabled={isLoading}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 mr-2 ${
                  isLoading
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : isDeepThink
                    ? 'bg-orange-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                }`}
                title={isDeepThink ? "Deep think mode enabled (o3)" : "Enable deep think mode (o3)"}
              >
                <Brain className="w-4 h-4" />
                Deep Think
              </button>
            )}
            <button
              onClick={onSubmit}
              disabled={!value.trim() || isLoading}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 ${
                !value.trim() || isLoading
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : isDeepThink
                  ? 'bg-orange-500 text-white hover:bg-orange-600 shadow-md'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md'
              }`}
            >
              <Send className="w-4 h-4" />
              {isLoading ? (isDeepThink ? 'Deep Thinking...' : 'Researching...') : 'Submit'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}