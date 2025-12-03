'use client';

import React, { useState } from 'react';
import TicketForm from '@/components/TicketForm';
import AgentResultsPanel from '@/components/AgentResultsPanel';
import { classifyTicket, classifyWithAnswers } from '@/lib/api';
import { AgentClassificationResult } from '@/types/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingAnswers, setIsLoadingAnswers] = useState(false);
  const [result, setResult] = useState<AgentClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (ticketText: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const classificationResult = await classifyTicket(ticketText);
      setResult(classificationResult);
    } catch (err) {
      setError('Ошибка при анализе заявки. Попробуйте еще раз.');
      console.error('Error classifying ticket:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitAnswers = async (answers: string[]) => {
    if (!result || !result.questions || !result.processed_text) {
      return;
    }

    setIsLoadingAnswers(true);
    setError(null);

    try {
      const finalResult = await classifyWithAnswers(
        result.processed_text,
        result.questions,
        answers
      );
      setResult(finalResult);
    } catch (err) {
      setError('Ошибка при обработке ответов. Попробуйте еще раз.');
      console.error('Error processing answers:', err);
    } finally {
      setIsLoadingAnswers(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <header className="bg-white border-b-2 border-blue-600 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-24 h-24 flex items-center justify-center">
              <img 
                src="/kfu_logo.svg" 
                alt="КФУ" 
                className="w-full h-full object-contain"
              />
            </div>
            <div className="border-l-2 border-blue-600 pl-4">
              <h1 className="text-xl font-semibold text-gray-900">
                Интеллектуальная классификация IT-заявок
              </h1>
              <p className="text-sm text-blue-600 font-medium">
                Multi-Agent система на базе ML + GigaChat
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8 bg-white rounded-lg shadow-sm border border-blue-100 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Как это работает?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 font-bold">
                1
              </div>
              <div>
                <p className="font-medium text-gray-900">Обработка</p>
                <p className="text-gray-600">Исправление аббревиатур</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 font-bold">
                2
              </div>
              <div>
                <p className="font-medium text-gray-900">ML анализ</p>
                <p className="text-gray-600">RuBERT + классификатор</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 font-bold">
                3
              </div>
              <div>
                <p className="font-medium text-gray-900">GigaChat</p>
                <p className="text-gray-600">Глубокий анализ</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 font-bold">
                4
              </div>
              <div>
                <p className="font-medium text-gray-900">Уточнение</p>
                <p className="text-gray-600">Доп. вопросы</p>
              </div>
            </div>
          </div>
        </div>

        <TicketForm onSubmit={handleAnalyze} isLoading={isLoading} />

        {error && (
          <div className="mt-6 bg-red-50 border-2 border-red-500 text-red-800 px-4 py-3 rounded-lg">
            <p className="font-medium">Ошибка</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-8">
            <AgentResultsPanel 
              result={result} 
              onSubmitAnswers={handleSubmitAnswers}
              isLoadingAnswers={isLoadingAnswers}
            />
          </div>
        )}
      </main>

      <footer className="mt-auto bg-white border-t border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2025 Казанский федеральный университет</p>
            <p className="text-blue-600 font-medium">Multi-Agent AI System v2.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
