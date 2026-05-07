type TaskFeedProps = {
  tasks: Array<{
    title: string;
    state: string;
    priority: number;
  }>;
};

export function TaskFeed({ tasks }: TaskFeedProps) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Task Feed</h2>
        <span className="text-sm text-ink/60">Priority queue</span>
      </div>
      <div className="overflow-hidden rounded-md border border-black/10 bg-white">
        {tasks.map((task) => (
          <div
            key={task.title}
            className="grid grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-black/10 px-4 py-3 last:border-b-0"
          >
            <span className="min-w-0 truncate text-sm font-medium text-ink">{task.title}</span>
            <span className="text-sm text-ink/60">{task.state}</span>
            <span className="w-10 text-right text-sm tabular-nums text-clay">{task.priority}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
