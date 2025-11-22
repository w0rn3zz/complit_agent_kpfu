import axios from 'axios';
import { 
  AnalysisResult, 
  TicketRequest, 
  AgentClassificationResult,
  TicketWithAnswersRequest 
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Новый метод для классификации через систему агентов
export const classifyTicket = async (ticketText: string): Promise<AgentClassificationResult> => {
  const request: TicketRequest = {
    text: ticketText,
    source: 'web_ui',
  };
  
  const response = await api.post<AgentClassificationResult>('/api/v1/classify', request);
  return response.data;
};

// Метод для финальной классификации с ответами
export const classifyWithAnswers = async (
  text: string,
  questions: string[],
  answers: string[]
): Promise<AgentClassificationResult> => {
  const request: TicketWithAnswersRequest = {
    text,
    questions,
    answers,
  };
  
  const response = await api.post<AgentClassificationResult>('/api/v1/classify-with-answers', request);
  return response.data;
};

// Старый метод для совместимости
export const analyzeTicket = async (ticketText: string): Promise<AnalysisResult> => {
  const request: TicketRequest = {
    text: ticketText,
    source: 'web_ui',
  };
  
  const response = await api.post<AnalysisResult>('/api/v1/analyze-text', request);
  return response.data;
};

export const getAgentsInfo = async () => {
  const response = await api.get('/api/v1/agents');
  return response.data;
};

export const getWorkTypes = async () => {
  const response = await api.get('/api/v1/work-types');
  return response.data;
};
