'use client';

import { useEffect, useState } from 'react';
import { AgentCard } from '@/components/AgentCard';
import { CommsStream } from '@/components/CommsStream';
import { TaskFeed } from '@/components/TaskFeed';
import { fetchAgents, fetchTasks } from '@/lib/api';
import { useStore } from '@/store/useStore';

export function DashboardClient() {
  const { agents, tasks, setAgents, setTasks } = useStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      try {
        const [nextAgents, nextTasks] = await Promise.all([fetchAgents(), fetchTasks()]);
        if (!cancelled) {
          setAgents(nextAgents);
          setTasks(nextTasks);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unable to load kernel state');
        }
      }
    }

    refresh();
    const interval = window.setInterval(refresh, 2000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [setAgents, setTasks]);

  return (
    <div className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-[1.1fr_0.9fr]">
      <section>
        {error ? (
          <div className="mb-4 rounded-md border border-clay/40 bg-white px-4 py-3 text-sm text-clay">
            {error}
          </div>
        ) : null}

        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Agents</h2>
          <span className="text-sm text-ink/60">{agents.length} registered</span>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {agents.length > 0 ? (
            agents.map((agent) => <AgentCard key={agent.id} agent={agent} />)
          ) : (
            <div className="rounded-md border border-black/10 bg-white p-4 text-sm text-ink/60">
              No agents registered yet.
            </div>
          )}
        </div>

        <div className="mt-6">
          <TaskFeed tasks={tasks} />
        </div>
      </section>

      <aside>
        <CommsStream />
      </aside>
    </div>
  );
}
