'use client';

import React from 'react';
import { AnalysisResult } from '@/types/api';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface ResultsPanelProps {
  result: AnalysisResult;
}

const categoryColors: Record<string, string> = {
  hardware: 'bg-orange-100 text-orange-800 border-orange-200',
  software: 'bg-blue-100 text-blue-800 border-blue-200',
  network: 'bg-green-100 text-green-800 border-green-200',
  access: 'bg-purple-100 text-purple-800 border-purple-200',
  consultation: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  other: 'bg-gray-100 text-gray-800 border-gray-200',
};

const priorityLabels: Record<string, string> = {
  critical: 'Критичный',
  high: 'Высокий',
  normal: 'Обычный',
  low: 'Низкий',
};

export default function ResultsPanel({ result }: ResultsPanelProps) {
  if (!result.is_relevant) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-900 mb-1">
              Заявка не относится к департаменту ИТ
            </h3>
            <p className="text-yellow-800">
              {result.metadata.message || 'Данная заявка не относится к компетенции департамента информатизации и связи.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-3">
          <CheckCircle className="w-6 h-6 text-green-600" />
          <h3 className="text-lg font-semibold text-green-900">
            Заявка обработана
          </h3>
        </div>
        <p className="text-sm text-green-800">
          Ваша заявка успешно классифицирована и будет направлена в соответствующий отдел.
        </p>
      </div>

      {result.matches.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border-2 border-blue-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Типы работ
          </h3>

          <div className="space-y-3">
            {result.matches.map((match, index) => (
              <div
                key={match.work_type_id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-2">
                      {match.work_type_name}
                    </h4>
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium border ${
                        categoryColors[match.category] || categoryColors.other
                      }`}
                    >
                      {match.category}
                    </span>
                  </div>

                  <div className="text-right ml-4">
                    <div className="text-2xl font-bold text-blue-600">
                      {(match.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-1.5 mb-3">
                  <div
                    className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${match.confidence * 100}%` }}
                  />
                </div>

                {match.reasoning && (
                  <p className="text-sm text-gray-600">{match.reasoning}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {result.metadata.routing && (
        <div className="bg-white rounded-lg shadow-sm border-2 border-blue-100 p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            Информация о маршрутизации
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">Приоритет</p>
              <p className="font-medium text-gray-900">
                {priorityLabels[result.metadata.routing.priority] || result.metadata.routing.priority}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Время выполнения</p>
              <p className="font-medium text-gray-900">
                {result.metadata.routing.estimated_time}
              </p>
            </div>
          </div>

          {result.metadata.routing.notes && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-1">Примечания</p>
              <p className="text-sm text-gray-900">{result.metadata.routing.notes}</p>
            </div>
          )}
        </div>
      )}

      {result.metadata.validation && !result.metadata.validation.is_complete && (
        <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            Требуется дополнительная информация
          </h3>

          {result.metadata.validation.suggested_questions && result.metadata.validation.suggested_questions.length > 0 && (
            <div>
              <p className="text-sm text-blue-800 mb-2">Пожалуйста, уточните:</p>
              <ul className="list-disc list-inside space-y-1 text-sm text-blue-900">
                {result.metadata.validation.suggested_questions.map((question, index) => (
                  <li key={index}>{question}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="text-sm text-blue-600 font-medium text-center">
        ID заявки: {result.ticket_id} • Обработано за {result.processing_time_ms}мс
      </div>
    </div>
  );
}
