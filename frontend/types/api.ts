export interface WorkTypeMatch {
  work_type_id: string;
  work_type_name: string;
  category: string;
  confidence: number;
  reasoning: string;
}

export interface AgentStep {
  agent_name: string;
  action: string;
  result: string;
  timestamp: string;
}

export interface AnalysisResult {
  ticket_id: string;
  is_relevant: boolean;
  matches: WorkTypeMatch[];
  agent_steps: AgentStep[];
  processing_time_ms: number;
  metadata: {
    validation?: {
      is_complete: boolean;
      missing_info: string[];
      suggested_questions: string[];
    };
    routing?: {
      priority: string;
      recommended_department: string;
      estimated_time: string;
      notes: string;
    };
    relevance_reason?: string;
    message?: string;
  };
}

// Новые типы для системы агентов
export interface AgentClassificationResult {
  stage: string;
  ticket_class?: string;
  confidence?: number;
  questions?: string[];
  processed_text?: string;
  reasoning?: string;
}

export interface TicketRequest {
  text: string;
  source?: string;
  external_id?: string;
  metadata?: Record<string, any>;
}

export interface TicketWithAnswersRequest {
  text: string;
  questions: string[];
  answers: string[];
}
