import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GraduationCap, Sparkles, CheckCircle, Lock, ChevronRight, Brain, Code, Users, Rocket } from 'lucide-react';
import { LearningStep } from './LearningStep';
import { ProgressTracker } from './ProgressTracker';
import { InteractiveExercise } from './InteractiveExercise';

export interface AILearningStep {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  content: string;
  exercise?: {
    type: 'prompt' | 'quiz' | 'build';
    question: string;
    hint?: string;
    validation?: (answer: string) => boolean;
  };
  completed: boolean;
  locked: boolean;
}

const learningSteps: AILearningStep[] = [
  {
    id: 'curiosity',
    title: 'Embrace Curiosity',
    subtitle: 'Start Playing',
    icon: <Sparkles className="w-6 h-6" />,
    content: `Get a subscription to an AI tool like ChatGPT Plus or Gemini, and dive in. Experiment by asking questions, ideating, and exploring possibilities. Let yourself be amazed, then challenge the AI to critique your ideas. This loop—ideation, excitement, critique—will expand your creative and analytical thinking.`,
    exercise: {
      type: 'prompt',
      question: 'Try asking me to help you brainstorm 5 creative uses for AI in your daily life. Then ask me to critique each idea!',
      hint: 'Think about tasks you do regularly that could be enhanced or automated.'
    },
    completed: false,
    locked: false
  },
  {
    id: 'custom-gpt',
    title: 'Build Your First Custom GPT',
    subtitle: 'Personalize Your AI',
    icon: <Brain className="w-6 h-6" />,
    content: `Move beyond generic chat interactions. Customize your AI by integrating a knowledge base (using RAG—Retrieval-Augmented Generation). Teach it specifics: your business, your expertise, your passions, or your strategies. This step personalizes AI, making it immediately useful, relevant, and deeply integrated into your workflow.`,
    exercise: {
      type: 'build',
      question: 'Design a custom AI assistant for a specific task. What role would it play? What knowledge would it need?',
      hint: 'Consider a repetitive task in your work or a hobby you\'re passionate about.'
    },
    completed: false,
    locked: true
  },
  {
    id: 'roles',
    title: 'Assign Roles and Personalities',
    subtitle: 'Transform AI into a Partner',
    icon: <Users className="w-6 h-6" />,
    content: `Use the system prompt creatively. Define specific roles for your AI—make it a coach for your hobby, a tutor for a challenging topic, or even a strategic advisor for your professional role. Custom roles enhance the depth and specificity of interactions, transforming your AI from a tool to a partner.`,
    exercise: {
      type: 'prompt',
      question: 'Ask me to act as a specific expert (e.g., "Act as a startup advisor" or "Be my fitness coach") and then engage with that persona.',
      hint: 'The more specific the role, the better the responses!'
    },
    completed: false,
    locked: true
  },
  {
    id: 'models',
    title: 'Understand Different AI Models',
    subtitle: 'Generative vs. Reasoning',
    icon: <Brain className="w-6 h-6" />,
    content: `Explore the fundamental differences:
    
• **Generative Models**: Great for creativity, content creation, and brainstorming.
• **Reasoning Models**: Best for deep problem-solving, complex queries, and methodical exploration.

Learning to choose the right model type enhances your efficiency and quality of outcomes.`,
    exercise: {
      type: 'quiz',
      question: 'Which type of model would be best for writing a creative story? And which for solving a complex math problem?',
      validation: (answer: string) => {
        const lower = answer.toLowerCase();
        return lower.includes('generative') && lower.includes('reasoning');
      }
    },
    completed: false,
    locked: true
  },
  {
    id: 'technical',
    title: 'Experiment with Technical Concepts',
    subtitle: 'Tokens and Context Windows',
    icon: <Code className="w-6 h-6" />,
    content: `Get familiar with how AI processes information:

• **Tokens**: Units of text and data the AI uses.
• **Context windows**: Limits on how much information the AI can process at once.

Understanding these basics empowers you to use AI more effectively, manage costs, and optimize results.`,
    exercise: {
      type: 'quiz',
      question: 'If an AI has a 4,000 token context window and each word is roughly 1.3 tokens, approximately how many words can it process?',
      validation: (answer: string) => {
        const num = parseInt(answer.replace(/[^0-9]/g, ''));
        return num >= 2800 && num <= 3200; // ~3,077 words
      }
    },
    completed: false,
    locked: true
  },
  {
    id: 'build',
    title: 'Build Something Meaningful',
    subtitle: 'Go Beyond Basics',
    icon: <Rocket className="w-6 h-6" />,
    content: `Once comfortable, challenge yourself to build something practical and inspiring. Whether it's a simple coding project, an interactive storytelling app, or an internal company tool, this step solidifies your knowledge, boosts your confidence, and provides tangible value.`,
    exercise: {
      type: 'build',
      question: 'Describe a simple AI-powered tool you could build to solve a real problem you face. What would it do? How would it help?',
      hint: 'Start small - even a simple automation or assistant can be valuable!'
    },
    completed: false,
    locked: true
  }
];

export function LearnAIModule({ onClose }: { onClose?: () => void }) {
  const [steps, setSteps] = useState(learningSteps);
  const [currentStep, setCurrentStep] = useState(0);
  const [showExercise, setShowExercise] = useState(false);

  useEffect(() => {
    // Load progress from localStorage
    const savedProgress = localStorage.getItem('ai-learning-progress');
    if (savedProgress) {
      const progress = JSON.parse(savedProgress);
      setSteps(progress.steps);
      setCurrentStep(progress.currentStep);
    }
  }, []);

  const saveProgress = (updatedSteps: AILearningStep[], stepIndex: number) => {
    localStorage.setItem('ai-learning-progress', JSON.stringify({
      steps: updatedSteps,
      currentStep: stepIndex,
      lastUpdated: new Date().toISOString()
    }));
  };

  const completeStep = (stepId: string) => {
    const updatedSteps = steps.map((step, index) => {
      if (step.id === stepId) {
        return { ...step, completed: true };
      }
      // Unlock next step
      if (index > 0 && steps[index - 1].id === stepId) {
        return { ...step, locked: false };
      }
      return step;
    });
    
    setSteps(updatedSteps);
    saveProgress(updatedSteps, currentStep);
    
    // Auto-advance to next step if available
    const nextIncompleteIndex = updatedSteps.findIndex(s => !s.completed && !s.locked);
    if (nextIncompleteIndex !== -1) {
      setTimeout(() => {
        setCurrentStep(nextIncompleteIndex);
        setShowExercise(false);
      }, 1500);
    }
  };

  const progress = (steps.filter(s => s.completed).length / steps.length) * 100;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-[#0a0a0a]/95 backdrop-blur-lg z-50 overflow-hidden"
    >
      <div className="h-full flex flex-col lg:flex-row">
        {/* Left Panel - Steps Navigation */}
        <div className="w-full lg:w-96 bg-[#111111] border-b lg:border-r lg:border-b-0 border-[#262626] overflow-y-auto">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-br from-[#0096FF]/20 to-purple-500/20 rounded-xl">
                  <GraduationCap className="w-6 h-6 text-[#0096FF]" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-[#E5E5E5]">Learn AI</h2>
                  <p className="text-xs text-[#666666]">Master AI step by step</p>
                </div>
              </div>
              {onClose && (
                <button
                  onClick={onClose}
                  className="text-[#666666] hover:text-[#E5E5E5] transition-colors"
                >
                  ×
                </button>
              )}
            </div>

            <ProgressTracker progress={progress} />

            <div className="space-y-3 mt-6">
              {steps.map((step, index) => (
                <motion.button
                  key={step.id}
                  onClick={() => !step.locked && setCurrentStep(index)}
                  disabled={step.locked}
                  className={`w-full p-4 rounded-lg border transition-all duration-200 text-left ${
                    currentStep === index
                      ? 'bg-[#0096FF]/10 border-[#0096FF]'
                      : step.completed
                      ? 'bg-green-500/10 border-green-500/20'
                      : step.locked
                      ? 'bg-[#0a0a0a] border-[#262626] opacity-50 cursor-not-allowed'
                      : 'bg-[#0a0a0a] border-[#262626] hover:border-[#0096FF]/50'
                  }`}
                  whileHover={!step.locked ? { scale: 1.02 } : {}}
                  whileTap={!step.locked ? { scale: 0.98 } : {}}
                >
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      step.completed
                        ? 'bg-green-500/20 text-green-500'
                        : currentStep === index
                        ? 'bg-[#0096FF]/20 text-[#0096FF]'
                        : 'bg-[#262626] text-[#666666]'
                    }`}>
                      {step.completed ? <CheckCircle className="w-5 h-5" /> : 
                       step.locked ? <Lock className="w-5 h-5" /> : 
                       step.icon}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-[#E5E5E5]">{step.title}</p>
                      <p className="text-xs text-[#666666]">{step.subtitle}</p>
                    </div>
                    {!step.locked && <ChevronRight className="w-4 h-4 text-[#666666]" />}
                  </div>
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Content & Exercise */}
        <div className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            {!showExercise ? (
              <LearningStep
                key={`step-${currentStep}`}
                step={steps[currentStep]}
                onStartExercise={() => setShowExercise(true)}
              />
            ) : (
              <InteractiveExercise
                key={`exercise-${currentStep}`}
                step={steps[currentStep]}
                onComplete={() => completeStep(steps[currentStep].id)}
                onBack={() => setShowExercise(false)}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}