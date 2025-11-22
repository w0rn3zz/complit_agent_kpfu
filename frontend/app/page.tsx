'use client';

import React, { useState } from 'react';
import TicketForm from '@/components/TicketForm';
import ResultsPanel from '@/components/ResultsPanel';
import { analyzeTicket } from '@/lib/api';
import { AnalysisResult } from '@/types/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (ticketText: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const analysisResult = await analyzeTicket(ticketText);
      setResult(analysisResult);
    } catch (err) {
      setError('Ошибка при анализе заявки. Попробуйте еще раз.');
      console.error('Error analyzing ticket:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b-2 border-blue-600">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img 
              src="/kfu_logo.svg" 
              alt="КФУ" 
              className="h-12"
            />
            <div className="border-l-2 border-blue-600 pl-4">
              <h1 className="text-xl font-semibold text-gray-900">
                Классификация IT-заявок
              </h1>
              <p className="text-sm text-blue-600 font-medium">
                Департамент информатизации и связи
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <TicketForm onSubmit={handleAnalyze} isLoading={isLoading} />

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8">
            <ResultsPanel result={result} />
          </div>
        )}
      </main>

      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>© 2025 Казанский федеральный университет</p>
            <p>Версия 1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
