import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Download, Sparkles, ChevronDown, ChevronUp, Maximize2, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  content: string;
  isStreaming?: boolean;
  onEnhancePrompt?: () => void;
}

export function ResponseDisplay({ content, isStreaming = false, onEnhancePrompt }: Props) {
  const [copiedStates, setCopiedStates] = useState<Record<number, boolean>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [isExpanded, setIsExpanded] = useState(false);
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();
  
  // Typing animation effect
  useEffect(() => {
    if (content !== displayedContent) {
      // If content is shorter than displayed (e.g., content was cleared), reset
      if (content.length < displayedContent.length) {
        setDisplayedContent(content);
        setCurrentIndex(content.length);
      } else if (content.length > currentIndex) {
        // Animate the new content with variable speed
        let lastTime = performance.now();
        const animate = (currentTime: number) => {
          const deltaTime = currentTime - lastTime;
          
          // Only update if enough time has passed (much slower for readable typing)
          if (deltaTime >= 50) { // ~20fps - very slow typing speed
            lastTime = currentTime;
            
            setCurrentIndex((prevIndex) => {
              // Calculate how many characters to add based on time passed
              const charsPerFrame = 1; // Much slower - only 1 character at a time
              const nextIndex = Math.min(prevIndex + charsPerFrame, content.length);
              setDisplayedContent(content.substring(0, nextIndex));
              
              if (nextIndex < content.length) {
                animationRef.current = requestAnimationFrame(animate);
              }
              return nextIndex;
            });
          } else {
            animationRef.current = requestAnimationFrame(animate);
          }
        };
        
        animationRef.current = requestAnimationFrame(animate);
      }
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [content, currentIndex, displayedContent, isStreaming]);
  
  // Keep scroll at top (don't auto-scroll to bottom)
  useEffect(() => {
    if (scrollRef.current && !isStreaming) {
      // Only scroll to top when new content starts
      if (displayedContent.length < 100) {
        scrollRef.current.scrollTop = 0;
      }
    }
  }, [displayedContent, isStreaming]);

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
    <>
      {/* Overlay */}
      {isExpanded && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300"
          onClick={() => setIsExpanded(false)}
        />
      )}
      
      {/* Main Container */}
      <div className={`${isExpanded ? 'fixed inset-8 z-50 shadow-2xl bg-white' : 'h-full bg-[#171717]'} flex flex-col overflow-hidden rounded-lg transition-all duration-300`}>
        {displayedContent && (
          <div className={`flex items-center justify-between p-4 border-b ${isExpanded ? 'border-gray-200' : 'border-[#262626]'} flex-shrink-0`}>
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
                className={`p-2 transition-colors ${isExpanded ? 'text-gray-600 hover:text-gray-900' : 'text-[#666666] hover:text-[#E5E5E5]'}`}
                title="Copy all"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleExport('markdown')}
                className={`p-2 transition-colors ${isExpanded ? 'text-gray-600 hover:text-gray-900' : 'text-[#666666] hover:text-[#E5E5E5]'}`}
                title="Export as Markdown"
              >
                <Download className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`p-2 transition-colors ${isExpanded ? 'text-gray-600 hover:text-gray-900' : 'text-[#666666] hover:text-[#E5E5E5]'}`}
                title={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? <X className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}
      
      <div ref={scrollRef} className={`flex-1 overflow-y-auto p-6 min-h-0 ${isExpanded ? 'max-w-4xl mx-auto' : ''}`}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className={`prose ${isExpanded ? 'prose-gray' : 'prose-invert'} max-w-none`}
        >
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeString = String(children).replace(/\n$/, '');
                
                return !inline && match ? (
                  <div className="relative group my-4">
                    <div className={`flex items-center justify-between px-4 py-2 rounded-t-lg ${isExpanded ? 'bg-gray-100' : 'bg-[#1e1e1e]'}`}>
                      <span className={`text-xs ${isExpanded ? 'text-gray-600' : 'text-[#666666]'}`}>{match[1]}</span>
                      <button
                        onClick={() => handleCopy(codeString)}
                        className={`transition-colors ${isExpanded ? 'text-gray-600 hover:text-gray-900' : 'text-[#666666] hover:text-[#E5E5E5]'}`}
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                    <div className={isExpanded ? 'bg-gray-50 p-4 rounded-b-lg overflow-x-auto' : ''}>
                      <SyntaxHighlighter
                        style={isExpanded ? undefined : vscDarkPlus}
                        language={match[1]}
                        PreTag="div"
                        className={`!mt-0 ${isExpanded ? '' : '!rounded-t-none'}`}
                        customStyle={isExpanded ? { background: 'transparent', padding: 0 } : {}}
                        {...props}
                      >
                        {codeString}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                ) : (
                  <code className={`px-1.5 py-0.5 rounded ${isExpanded ? 'bg-gray-100 text-gray-900' : 'bg-[#1e1e1e] text-[#E5E5E5]'}`} {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({ children }) => (
                <h1 className={`text-2xl font-bold mb-4 ${isExpanded ? 'text-gray-900' : 'text-[#E5E5E5]'}`}>{children}</h1>
              ),
              h2: ({ children }) => {
                const id = String(children).toLowerCase().replace(/\s+/g, '-');
                const isExpanded = expandedSections[id] !== false;
                
                return (
                  <div className="my-4">
                    <button
                      onClick={() => toggleSection(id)}
                      className={`flex items-center gap-2 text-xl font-semibold hover:text-[#0096FF] transition-colors ${isExpanded ? 'text-gray-900' : 'text-[#E5E5E5]'}`}
                    >
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
                      {children}
                    </button>
                  </div>
                );
              },
              h3: ({ children }) => (
                <h3 className={`text-lg font-semibold mb-2 ${isExpanded ? 'text-gray-900' : 'text-[#E5E5E5]'}`}>{children}</h3>
              ),
              p: ({ children }) => (
                <p className={`mb-4 leading-relaxed ${isExpanded ? 'text-gray-700' : 'text-[#E5E5E5]'}`}>{children}</p>
              ),
              ul: ({ children }) => (
                <ul className={`list-disc list-inside mb-4 space-y-1 ${isExpanded ? 'text-gray-700' : 'text-[#E5E5E5]'}`}>{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className={`list-decimal list-inside mb-4 space-y-1 ${isExpanded ? 'text-gray-700' : 'text-[#E5E5E5]'}`}>{children}</ol>
              ),
              blockquote: ({ children }) => (
                <blockquote className={`border-l-4 border-[#0096FF] pl-4 my-4 italic ${isExpanded ? 'text-gray-600' : 'text-[#A3A3A3]'}`}>
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
            {displayedContent}
          </ReactMarkdown>
        </motion.div>
        
        {(isStreaming || currentIndex < content.length) && (
          <div className="inline-block mt-2">
            <motion.div
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className={`w-2 h-5 ${isExpanded ? 'bg-gray-600' : 'bg-[#0096FF]'}`}
            />
          </div>
        )}
      </div>
      </div>
    </>
  );
}