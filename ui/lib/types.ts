export type Agent = {
  id: string;
  name: string;
  type: string;
  status: string;
  system_prompt: string;
  model: string;
  config_jsonb: Record<string, unknown>;
  sandbox_container_id: string | null;
  token_budget_daily: number | null;
  tokens_used_today: number;
  last_heartbeat_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Task = {
  id: string;
  agent_id: string;
  parent_task_id: string | null;
  priority: number;
  state: string;
  payload_jsonb: Record<string, unknown>;
  result_jsonb: Record<string, unknown> | null;
  error_text: string | null;
  token_budget: number;
  tokens_used: number;
  arq_job_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AgentSpec = {
  name: string;
  type: string;
  system_prompt: string;
  model: string;
  config: Record<string, unknown>;
  token_budget_daily: number | null;
};

export type TaskSpec = {
  payload: Record<string, unknown>;
  priority?: number;
  estimated_tokens?: number;
  parent_task_id?: string | null;
};
