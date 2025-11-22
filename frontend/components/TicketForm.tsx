'use client';

import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface TicketFormProps {
  onSubmit: (text: string) => void;
  isLoading: boolean;
}

export default function TicketForm({ onSubmit, isLoading }: TicketFormProps) {
  const [ticketText, setTicketText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticketText.trim()) {
      onSubmit(ticketText);
    }
  };

  const exampleTickets = [
    'Не работает компьютер в аудитории 301',
    'Нужно установить Microsoft Office',
    'Забыл пароль от учетной записи',
    'Нет интернета в кабинете 205',
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border-2 border-blue-100 p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="ticket-text" className="block text-sm font-medium text-gray-700 mb-2">
            Опишите вашу проблему или запрос
          </label>
          <textarea
            id="ticket-text"
            value={ticketText}
            onChange={(e) => setTicketText(e.target.value)}
            placeholder="Например: Не работает принтер в аудитории 301..."
            className="w-full h-32 px-4 py-3 border-2 border-gray-200 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-900"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !ticketText.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium py-3 px-6 rounded-md flex items-center justify-center gap-2 transition-colors shadow-sm hover:shadow-md"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Анализируем заявку...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Отправить заявку
            </>
          )}
        </button>
      </form>

      <div className="mt-6 pt-6 border-t-2 border-blue-100">
        <p className="text-sm font-medium text-gray-700 mb-3">
          Примеры заявок:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {exampleTickets.map((example, index) => (
            <button
              key={index}
              onClick={() => setTicketText(example)}
              disabled={isLoading}
              className="text-left px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md text-sm text-gray-700 transition-colors disabled:opacity-50"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
