export type HealthPayload = {
  status: string;
  app: string;
  environment: string;
  uptime_seconds: number;
  agent_count: number;
  redis: string;
};

export async function fetchHealth(): Promise<HealthPayload> {
  const response = await fetch('/api/proxy/health', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`health request failed: ${response.status}`);
  }
  return response.json() as Promise<HealthPayload>;
}
