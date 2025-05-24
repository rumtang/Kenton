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
    if (name.includes('gpt-4.1') && !name.includes('mini')) return 'text-purple-600 border-purple-200 bg-purple-50';
    if (name.includes('gpt-4.1-mini')) return 'text-blue-600 border-blue-200 bg-blue-50';
    if (name.includes('gpt-4o')) return 'text-emerald-600 border-emerald-200 bg-emerald-50';
    if (name.includes('o1') || name.includes('o3')) return 'text-green-600 border-green-200 bg-green-50';
    if (name.includes('embedding')) return 'text-yellow-600 border-yellow-200 bg-yellow-50';
    return 'text-gray-600 border-gray-200 bg-gray-50';
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
                <p className="font-medium text-gray-900">{model.name}</p>
                <p className="text-sm text-gray-600 mt-1">{model.purpose}</p>
                {model.tokensUsed !== undefined && model.tokensUsed > 0 && (
                  <div className="flex items-center gap-2 mt-2">
                    <Zap className="w-3 h-3 text-gray-500" />
                    <span className="text-xs text-gray-500">
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
        <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Total Tokens Used</span>
            <span className="text-sm font-mono text-gray-900">{totalTokens.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-gray-500">Estimated Cost</span>
            <span className="text-sm font-mono text-green-400">
              ${(totalTokens * 0.00002).toFixed(4)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}