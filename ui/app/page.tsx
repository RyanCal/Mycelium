import { AgentCard } from '@/components/AgentCard';
import { CommsStream } from '@/components/CommsStream';
import { TaskFeed } from '@/components/TaskFeed';

const agents = [
  { name: 'echo-default', status: 'idle', type: 'echo', budget: '0 / unlimited' },
  { name: 'researcher', status: 'planned', type: 'researcher', budget: 'Phase 2' },
  { name: 'reviewer', status: 'planned', type: 'reviewer', budget: 'Phase 2' },
];

const tasks = [
  { title: 'Bootstrap kernel scaffold', state: 'complete', priority: 80 },
  { title: 'Echo worker flow', state: 'phase 1', priority: 60 },
  { title: 'Cold memory search', state: 'phase 2', priority: 45 },
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-black/10 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-normal text-ink">Mycelium</h1>
            <p className="mt-1 text-sm text-ink/65">Kernel operations dashboard</p>
          </div>
          <div className="rounded-md border border-black/10 px-3 py-2 text-sm text-moss">
            Phase 0 bootstrap
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-[1.1fr_0.9fr]">
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Agents</h2>
            <span className="text-sm text-ink/60">{agents.length} registered views</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {agents.map((agent) => (
              <AgentCard key={agent.name} agent={agent} />
            ))}
          </div>

          <div className="mt-6">
            <TaskFeed tasks={tasks} />
          </div>
        </section>

        <aside>
          <CommsStream />
        </aside>
      </div>
    </main>
  );
}
