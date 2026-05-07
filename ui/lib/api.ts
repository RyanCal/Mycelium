import type { Agent, AgentSpec, Task, TaskSpec } from '@/lib/types';

export type HealthPayload = {
  status: string;
  app: string;
  environment: string;
  uptime_seconds: number;
  agent_count: number;
  redis: string;
};

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/proxy${path}`, {
    ...init,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthPayload> {
  return requestJson<HealthPayload>('/health');
}

export async function fetchAgents(): Promise<Agent[]> {
  return requestJson<Agent[]>('/api/v1/agents');
}

export async function fetchTasks(): Promise<Task[]> {
  return requestJson<Task[]>('/api/v1/tasks');
}

export async function fetchTask(id: string): Promise<Task> {
  return requestJson<Task>(`/api/v1/tasks/${id}`);
}

export async function postAgent(spec: AgentSpec): Promise<Agent> {
  return requestJson<Agent>('/api/v1/agents', {
    method: 'POST',
    body: JSON.stringify(spec),
  });
}

export async function postTask(agentId: string, spec: TaskSpec): Promise<Task> {
  return requestJson<Task>(`/api/v1/agents/${agentId}/tasks`, {
    method: 'POST',
    body: JSON.stringify(spec),
  });
}
