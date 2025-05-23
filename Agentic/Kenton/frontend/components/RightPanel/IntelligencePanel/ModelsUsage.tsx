import React from 'react';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

interface Model {
  name: string;
  purpose: string;
  tokensUsed?: number;
}

interface Props {
  models: Model[];
}

export function ModelsUsage({ models }: Props) {
  const getModelIcon = (name: string) => {
    if (name.includes('gpt-4.1') && !name.includes('mini')) return '🧠';
    if (name.includes('gpt-4.1-mini')) return '⚡';
    if (name.includes('gpt-4o')) return '🚀';
    if (name.includes('o1') || name.includes('o3')) return '🎯';
    if (name.includes('embedding')) return '🔢';
    return '🤖';
  };

  const getModelColor = (name: string) => {
    if (name.includes('gpt-4.1') && !name.includes('mini')) return 'text-purple-500 border-purple-500/20 bg-purple-500/10';
    if (name.includes('gpt-4.1-mini')) return 'text-blue-500 border-blue-500/20 bg-blue-500/10';
    if (name.includes('gpt-4o')) return 'text-emerald-500 border-emerald-500/20 bg-emerald-500/10';
    if (name.includes('o1') || name.includes('o3')) return 'text-green-500 border-green-500/20 bg-green-500/10';
    if (name.includes('embedding')) return 'text-yellow-500 border-yellow-500/20 bg-yellow-500/10';
    return 'text-gray-500 border-gray-500/20 bg-gray-500/10';
  };

  const totalTokens = models.reduce((sum, model) => sum + (model.tokensUsed || 0), 0);

  return (
    <div className="space-y-3">
      {models.map((model, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
          className={`rounded-lg p-4 border ${getModelColor(model.name)}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <span className="text-2xl mt-0.5">{getModelIcon(model.name)}</span>
              <div>
                <p className="font-medium text-[#E5E5E5]">{model.name}</p>
                <p className="text-sm text-[#A3A3A3] mt-1">{model.purpose}</p>
                {model.tokensUsed && (
                  <div className="flex items-center gap-2 mt-2">
                    <Zap className="w-3 h-3 text-[#666666]" />
                    <span className="text-xs text-[#666666]">
                      {model.tokensUsed.toLocaleString()} tokens
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      ))}
      
      {totalTokens > 0 && (
        <div className="mt-4 p-3 bg-[#111111] rounded-lg border border-[#262626]">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#666666]">Total Tokens Used</span>
            <span className="text-sm font-mono text-[#E5E5E5]">{totalTokens.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-[#666666]">Estimated Cost</span>
            <span className="text-sm font-mono text-green-400">
              ${(totalTokens * 0.00002).toFixed(4)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}