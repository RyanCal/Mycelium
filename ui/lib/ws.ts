export function taskStreamUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
  return `${base.replace(/^http/, 'ws')}/api/v1/tasks/stream`;
}
