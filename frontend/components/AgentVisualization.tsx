'use client';

import React from 'react';
import { AgentStep } from '@/types/api';
import { motion } from 'framer-motion';
import { Bot, CheckCircle, Loader2 } from 'lucide-react';

interface AgentVisualizationProps {
  steps: AgentStep[];
  isProcessing?: boolean;
}

const agentIcons: Record<string, string> = {
  ClassifierAgent: '🔍',
  RelevanceAgent: '✓',
  ConfidenceAgent: '📊',
  ValidatorAgent: '✔',
  RouterAgent: '🎯',
  ExplanationAgent: '💡',
};

const agentColors: Record<string, string> = {
  ClassifierAgent: 'bg-blue-100 border-blue-300',
  RelevanceAgent: 'bg-green-100 border-green-300',
  ConfidenceAgent: 'bg-purple-100 border-purple-300',
  ValidatorAgent: 'bg-yellow-100 border-yellow-300',
  RouterAgent: 'bg-orange-100 border-orange-300',
  ExplanationAgent: 'bg-pink-100 border-pink-300',
};

export default function AgentVisualization({ steps, isProcessing }: AgentVisualizationProps) {
  if (steps.length === 0 && !isProcessing) {
    return null;
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-3 mb-6">
          <Bot className="w-6 h-6 text-blue-600" />
          <h3 className="text-xl font-semibold text-gray-800">
            Работа AI агентов
          </h3>
          {isProcessing && (
            <Loader2 className="w-5 h-5 text-blue-600 animate-spin ml-auto" />
          )}
        </div>

        <div className="space-y-3">
          {steps.map((step, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`border-2 rounded-lg p-4 ${
                agentColors[step.agent_name] || 'bg-gray-100 border-gray-300'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="text-2xl">{agentIcons[step.agent_name] || '🤖'}</div>

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-gray-800">{step.agent_name}</h4>
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>

                  <p className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">Действие:</span> {step.action}
                  </p>

                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Результат:</span> {step.result}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}

          {isProcessing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="border-2 border-dashed border-blue-300 bg-blue-50 rounded-lg p-4"
            >
              <div className="flex items-center gap-3">
                <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
                <p className="text-gray-700">Агенты обрабатывают заявку...</p>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
