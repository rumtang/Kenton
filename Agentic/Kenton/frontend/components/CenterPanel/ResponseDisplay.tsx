import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Download, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  content: string;
  isStreaming?: boolean;
  onEnhancePrompt?: () => void;
}

export function ResponseDisplay({ content, isStreaming = false, onEnhancePrompt }: Props) {
  const [copiedStates, setCopiedStates] = useState<Record<number, boolean>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll when streaming
  useEffect(() => {
    if (isStreaming && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [content, isStreaming]);

  const handleCopy = async (text: string, index?: number) => {
    await navigator.clipboard.writeText(text);
    if (index !== undefined) {
      setCopiedStates({ ...copiedStates, [index]: true });
      setTimeout(() => {
        setCopiedStates({ ...copiedStates, [index]: false });
      }, 2000);
    }
  };

  const handleExport = (format: 'pdf' | 'markdown' | 'text') => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-${Date.now()}.${format === 'markdown' ? 'md' : format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleSection = (id: string) => {
    setExpandedSections(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {content && (
        <div className="flex items-center justify-between p-4 border-b border-[#262626] flex-shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={onEnhancePrompt}
              className="px-3 py-1.5 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 text-yellow-400 rounded-lg text-sm flex items-center gap-2 hover:from-yellow-500/30 hover:to-orange-500/30 transition-all duration-200"
            >
              <Sparkles className="w-4 h-4" />
              Enhance this prompt
            </button>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleCopy(content)}
              className="p-2 text-[#666666] hover:text-[#E5E5E5] transition-colors"
              title="Copy all"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleExport('markdown')}
              className="p-2 text-[#666666] hover:text-[#E5E5E5] transition-colors"
              title="Export as Markdown"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 min-h-0">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="prose prose-invert max-w-none"
        >
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeString = String(children).replace(/\n$/, '');
                
                return !inline && match ? (
                  <div className="relative group my-4">
                    <div className="flex items-center justify-between bg-[#1e1e1e] px-4 py-2 rounded-t-lg">
                      <span className="text-xs text-[#666666]">{match[1]}</span>
                      <button
                        onClick={() => handleCopy(codeString)}
                        className="text-[#666666] hover:text-[#E5E5E5] transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      className="!mt-0 !rounded-t-none"
                      {...props}
                    >
                      {codeString}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <code className="bg-[#1e1e1e] px-1.5 py-0.5 rounded text-[#E5E5E5]" {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({ children }) => (
                <h1 className="text-2xl font-bold text-[#E5E5E5] mb-4">{children}</h1>
              ),
              h2: ({ children }) => {
                const id = String(children).toLowerCase().replace(/\s+/g, '-');
                const isExpanded = expandedSections[id] !== false;
                
                return (
                  <div className="my-4">
                    <button
                      onClick={() => toggleSection(id)}
                      className="flex items-center gap-2 text-xl font-semibold text-[#E5E5E5] hover:text-[#0096FF] transition-colors"
                    >
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                      {children}
                    </button>
                  </div>
                );
              },
              h3: ({ children }) => (
                <h3 className="text-lg font-semibold text-[#E5E5E5] mb-2">{children}</h3>
              ),
              p: ({ children }) => (
                <p className="text-[#E5E5E5] mb-4 leading-relaxed">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-inside text-[#E5E5E5] mb-4 space-y-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside text-[#E5E5E5] mb-4 space-y-1">{children}</ol>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-[#0096FF] pl-4 my-4 text-[#A3A3A3] italic">
                  {children}
                </blockquote>
              ),
              a: ({ href, children }) => (
                <a href={href} className="text-[#0096FF] hover:underline" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </motion.div>
        
        {isStreaming && (
          <div className="inline-block mt-2">
            <motion.div
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-5 bg-[#0096FF]"
            />
          </div>
        )}
      </div>
    </div>
  );
}