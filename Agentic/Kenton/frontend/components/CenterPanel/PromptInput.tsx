import React, { useRef, useEffect, useState } from 'react';
import { Send, X, Sparkles, Wand2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Props {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onEnhancePrompt: () => void;
  isLoading?: boolean;
  showPromptLoadedAnimation?: boolean;
}

export function PromptInput({ value, onChange, onSubmit, onEnhancePrompt, isLoading = false, showPromptLoadedAnimation = false }: Props) {
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

      <div className={`relative bg-[#111111] rounded-xl border-2 transition-all duration-200 ${
        isFocused ? 'border-[#0096FF] shadow-lg shadow-[#0096FF]/20' : 'border-[#262626]'
      }`}>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Explore something..."
          className="w-full px-6 py-4 bg-transparent text-[#E5E5E5] placeholder-[#666666] resize-none focus:outline-none"
          style={{ minHeight: '60px' }}
          disabled={isLoading}
        />
        
        <div className="flex items-center justify-between px-6 py-3 border-t border-[#262626]">
          <div className="flex items-center gap-4">
            <span className={`text-xs ${value.length > charLimit * 0.9 ? 'text-red-400' : 'text-[#666666]'}`}>
              {value.length} / {charLimit}
            </span>
            <span className="text-xs text-[#666666]">
              {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'} + Enter to submit
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            {value && (
              <button
                onClick={() => onChange('')}
                className="p-2 text-[#666666] hover:text-[#E5E5E5] transition-colors"
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
                  ? 'bg-[#262626] text-[#666666] cursor-not-allowed'
                  : 'bg-purple-600 text-white hover:bg-purple-700 shadow-lg shadow-purple-600/20'
              }`}
              title="Enhance this prompt"
            >
              <Wand2 className="w-4 h-4" />
              Enhance
            </button>
            <button
              onClick={onSubmit}
              disabled={!value.trim() || isLoading}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 ${
                !value.trim() || isLoading
                  ? 'bg-[#262626] text-[#666666] cursor-not-allowed'
                  : 'bg-[#0096FF] text-white hover:bg-[#0080DD] shadow-lg shadow-[#0096FF]/20'
              }`}
            >
              <Send className="w-4 h-4" />
              {isLoading ? 'Researching...' : 'Submit'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}