'use client';

import React, { useState } from 'react';
import { AgentClassificationResult } from '@/types/api';
import { CheckCircle, HelpCircle, Loader2, Send } from 'lucide-react';

interface AgentResultsPanelProps {
  result: AgentClassificationResult;
  onSubmitAnswers?: (answers: string[]) => void;
  isLoadingAnswers?: boolean;
}

export default function AgentResultsPanel({ 
  result, 
  onSubmitAnswers,
  isLoadingAnswers = false 
}: AgentResultsPanelProps) {
  const [answers, setAnswers] = useState<string[]>(
    result.questions ? new Array(result.questions.length).fill('') : []
  );

  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    if (onSubmitAnswers && answers.every(a => a.trim())) {
      onSubmitAnswers(answers);
    }
  };

  const getStageLabel = (stage: string) => {
    const labels: Record<string, string> = {
      'abbreviation_convert': 'Обработка аббревиатур',
      'ml_classification': 'ML классификация',
      'deep_analysis': 'Глубокий анализ',
      'question_generation': 'Требуется уточнение',
      'final_analysis': 'Финальный анализ',
      'completed': 'Завершено'
    };
    return labels[stage] || stage;
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-600';
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Если есть вопросы и стадия требует уточнения - показываем форму
  if (result.questions && result.questions.length > 0 && result.stage === 'question_generation') {
    return (
      <div className="space-y-6">
        <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <HelpCircle className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-blue-900">
              Требуется дополнительная информация
            </h3>
          </div>

          <p className="text-sm text-blue-800 mb-2">
            Пожалуйста, ответьте на следующие вопросы для точной классификации заявки:
          </p>

          {result.ticket_class && (
            <div className="bg-blue-100 border border-blue-300 rounded-md p-3 mb-4">
              <p className="text-xs text-blue-700 font-medium">Предварительная классификация:</p>
              <p className="text-sm text-blue-900">{result.ticket_class}</p>
              {result.confidence && (
                <p className="text-xs text-blue-600 mt-1">
                  Уверенность: {(result.confidence * 100).toFixed(0)}% (требуется уточнение)
                </p>
              )}
            </div>
          )}

          <div className="space-y-4">
            {result.questions.map((question, index) => (
              <div key={index} className="bg-white rounded-lg p-4 border border-blue-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {index + 1}. {question}
                </label>
                <input
                  type="text"
                  value={answers[index] || ''}
                  onChange={(e) => handleAnswerChange(index, e.target.value)}
                  placeholder="Введите ваш ответ..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400"
                  disabled={isLoadingAnswers}
                />
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isLoadingAnswers || !answers.every(a => a.trim())}
            className="mt-6 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-md flex items-center justify-center gap-2 transition-colors"
          >
            {isLoadingAnswers ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Обработка ответов...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Отправить ответы
              </>
            )}
          </button>
        </div>

        {result.reasoning && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-600">
              <strong>Примечание:</strong> {result.reasoning}
            </p>
          </div>
        )}
      </div>
    );
  }

  // Если класс определен - показываем результат
  if (result.ticket_class && result.ticket_class !== 'нет классов') {
    return (
      <div className="space-y-6">
        <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-semibold text-green-900">
              Заявка классифицирована
            </h3>
          </div>

          <div className="mt-4 space-y-3">
            <div>
              <p className="text-sm text-green-700 mb-1">Класс заявки:</p>
              <p className="text-lg font-semibold text-green-900">
                {result.ticket_class}
              </p>
            </div>

            {result.confidence !== undefined && (
              <div>
                <p className="text-sm text-green-700 mb-2">Уверенность:</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${
                        result.confidence >= 0.9 ? 'bg-green-600' :
                        result.confidence >= 0.7 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                  <span className={`text-2xl font-bold ${getConfidenceColor(result.confidence)}`}>
                    {(result.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            )}

            <div>
              <p className="text-sm text-green-700 mb-1">Этап обработки:</p>
              <p className="text-sm font-medium text-green-900">
                {getStageLabel(result.stage)}
              </p>
            </div>

            {result.reasoning && (
              <div className="pt-3 border-t border-green-200">
                <p className="text-sm text-green-700 mb-1">Обоснование:</p>
                <p className="text-sm text-green-900">{result.reasoning}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Если класс не определен
  return (
    <div className="bg-yellow-50 border-2 border-yellow-500 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-3">
        <HelpCircle className="w-6 h-6 text-yellow-600" />
        <h3 className="text-lg font-semibold text-yellow-900">
          Не удалось классифицировать заявку
        </h3>
      </div>

      <p className="text-sm text-yellow-800 mb-3">
        К сожалению, система не смогла определить подходящий класс для данной заявки.
      </p>

      {result.reasoning && (
        <div className="mt-4 pt-4 border-t border-yellow-200">
          <p className="text-sm text-yellow-700 mb-1">Причина:</p>
          <p className="text-sm text-yellow-900">{result.reasoning}</p>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-yellow-200">
        <p className="text-sm text-yellow-800">
          Пожалуйста, свяжитесь с техподдержкой напрямую для решения вашей проблемы.
        </p>
      </div>
    </div>
  );
}
