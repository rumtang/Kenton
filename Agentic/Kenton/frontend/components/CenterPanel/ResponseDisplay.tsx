import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Download, Sparkles, ChevronDown, ChevronUp, Maximize2, X, CheckCircle, MessageSquare, Send } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
  content: string;
  isStreaming?: boolean;
  onEnhancePrompt?: () => void;
  onFollowUp?: (question: string) => void;
}

export function ResponseDisplay({ content, isStreaming = false, onEnhancePrompt, onFollowUp }: Props) {
  const [copiedStates, setCopiedStates] = useState<Record<number, boolean>>({});
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  const [isExpanded, setIsExpanded] = useState(false);
  const [displayedContent, setDisplayedContent] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [followUpQuestion, setFollowUpQuestion] = useState('');
  const [showFollowUp, setShowFollowUp] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const followUpInputRef = useRef<HTMLTextAreaElement>(null);
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
      <div className={`${isExpanded ? 'fixed inset-8 z-50 shadow-2xl bg-white' : 'h-full bg-gradient-to-b from-white to-gray-50'} flex flex-col rounded-lg transition-all duration-300`}>
        {displayedContent && (
          <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 flex-shrink-0">
            <div className="flex items-center gap-4">
              <button
                onClick={onEnhancePrompt}
                className="px-4 py-2 bg-gradient-to-r from-amber-50 to-orange-50 text-orange-700 rounded-lg text-sm font-medium flex items-center gap-2 hover:from-amber-100 hover:to-orange-100 transition-all duration-200 border border-orange-200 shadow-sm hover:shadow"
              >
                <Sparkles className="w-4 h-4" />
                Enhance this prompt
              </button>
            </div>
            
            <div className="flex items-center gap-1">
              <button
                onClick={() => handleCopy(content)}
                className="p-2 rounded-lg transition-all text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                title="Copy all"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleExport('markdown')}
                className="p-2 rounded-lg transition-all text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                title="Export as Markdown"
              >
                <Download className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-2 rounded-lg transition-all text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                title={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? <X className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}
      
      <div ref={scrollRef} className={`flex-1 overflow-y-auto overflow-x-hidden p-8 ${isExpanded ? 'max-w-5xl mx-auto' : ''}`}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="prose prose-lg max-w-none prose-headings:font-semibold prose-p:text-gray-700 prose-p:leading-relaxed prose-strong:text-gray-900 prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline prose-pre:bg-transparent prose-pre:p-0"
        >
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeString = String(children).replace(/\n$/, '');
                
                return !inline && match ? (
                  <div className="relative group my-6 rounded-xl overflow-hidden shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between px-4 py-2.5 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                      <span className="text-sm font-medium text-gray-700">{match[1]}</span>
                      <button
                        onClick={() => handleCopy(codeString, props.key as number)}
                        className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 bg-white rounded-md border border-gray-200 hover:border-gray-300 transition-all"
                      >
                        {copiedStates[props.key as number] ? (
                          <>
                            <CheckCircle className="w-3.5 h-3.5 text-green-600" />
                            <span className="text-green-600">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <div className="bg-gray-900 p-4 overflow-x-auto">
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        className="!mt-0 text-sm"
                        customStyle={{ background: 'transparent', padding: 0, margin: 0 }}
                        {...props}
                      >
                        {codeString}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                ) : (
                  <code className="px-2 py-1 rounded-md bg-gray-100 text-gray-800 font-mono text-sm border border-gray-200" {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({ children }) => (
                <h1 className="text-3xl font-bold mb-6 text-gray-900 tracking-tight border-b border-gray-200 pb-3">{children}</h1>
              ),
              h2: ({ children }) => {
                const id = String(children).toLowerCase().replace(/\s+/g, '-');
                const isExpanded = expandedSections[id] !== false;
                
                return (
                  <div className="my-6 group">
                    <button
                      onClick={() => toggleSection(id)}
                      className="flex items-center gap-2 text-2xl font-semibold hover:text-blue-600 transition-colors text-gray-900"
                    >
                      <span className="flex items-center justify-center w-6 h-6 rounded-md bg-gray-100 group-hover:bg-blue-100 transition-colors">
                        {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                      </span>
                      {children}
                    </button>
                  </div>
                );
              },
              h3: ({ children }) => (
                <h3 className="text-xl font-semibold mb-3 mt-5 text-gray-800">{children}</h3>
              ),
              p: ({ children }) => (
                <p className="mb-5 leading-7 text-gray-700">{children}</p>
              ),
              ul: ({ children }) => (
                <ul className="mb-5 space-y-2 text-gray-700">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="mb-5 space-y-2 text-gray-700">{children}</ol>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-blue-500 pl-6 my-6 italic text-gray-600 bg-blue-50 py-4 pr-6 rounded-r-lg">
                  {children}
                </blockquote>
              ),
              a: ({ href, children }) => (
                <a href={href} className="text-blue-600 hover:text-blue-800 font-medium transition-colors border-b border-transparent hover:border-blue-300" target="_blank" rel="noopener noreferrer">
                  {children}
                </a>
              ),
              li: ({ children }) => (
                <li className="flex items-start">
                  <span className="inline-block w-1.5 h-1.5 bg-blue-500 rounded-full mt-2.5 mr-3 flex-shrink-0"></span>
                  <span className="flex-1">{children}</span>
                </li>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-gray-900">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-gray-800">{children}</em>
              ),
              hr: () => (
                <hr className="my-8 border-gray-200" />
              ),
              table: ({ children }) => (
                <div className="my-6 overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                    {children}
                  </table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-gray-50">{children}</thead>
              ),
              th: ({ children }) => (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-6 py-4 text-sm text-gray-700 border-t border-gray-200">
                  {children}
                </td>
              ),
            }}
          >
            {displayedContent}
          </ReactMarkdown>
        </motion.div>
        
        {(isStreaming || currentIndex < content.length) && (
          <div className="inline-flex items-center gap-2 mt-4">
            <motion.div
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-2 bg-blue-600 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
              className="w-2 h-2 bg-blue-600 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
              className="w-2 h-2 bg-blue-600 rounded-full"
            />
          </div>
        )}
      </div>
      
      {/* Follow-up Section */}
      {!isStreaming && displayedContent && onFollowUp && (
        <div className="border-t border-gray-200 bg-gray-50 p-6">
          <div className="max-w-4xl mx-auto">
            {!showFollowUp ? (
              <button
                onClick={() => {
                  setShowFollowUp(true);
                  setTimeout(() => followUpInputRef.current?.focus(), 100);
                }}
                className="w-full text-left p-4 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 transition-colors flex items-center gap-3 group"
              >
                <MessageSquare className="w-5 h-5 text-gray-400 group-hover:text-gray-600" />
                <span className="text-gray-500 group-hover:text-gray-700">Ask a follow-up question about this response...</span>
              </button>
            ) : (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Follow-up Question
                </label>
                <div className="flex gap-3">
                  <textarea
                    ref={followUpInputRef}
                    value={followUpQuestion}
                    onChange={(e) => setFollowUpQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey && followUpQuestion.trim()) {
                        e.preventDefault();
                        onFollowUp(followUpQuestion);
                        setFollowUpQuestion('');
                        setShowFollowUp(false);
                      }
                    }}
                    placeholder="What would you like to know more about?"
                    className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={2}
                  />
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => {
                        if (followUpQuestion.trim()) {
                          onFollowUp(followUpQuestion);
                          setFollowUpQuestion('');
                          setShowFollowUp(false);
                        }
                      }}
                      disabled={!followUpQuestion.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Ask
                    </button>
                    <button
                      onClick={() => {
                        setShowFollowUp(false);
                        setFollowUpQuestion('');
                      }}
                      className="px-4 py-2 text-gray-600 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
                <p className="text-xs text-gray-500">Press Enter to send, Shift+Enter for new line</p>
              </motion.div>
            )}
          </div>
        </div>
      )}
      </div>
    </>
  );
}