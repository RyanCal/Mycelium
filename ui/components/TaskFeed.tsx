import type { Task } from '@/lib/types';

type TaskFeedProps = {
  tasks: Task[];
};

function taskTitle(task: Task): string {
  const message = task.payload_jsonb.message;
  if (typeof message === 'string') {
    return message;
  }
  return task.id;
}

export function TaskFeed({ tasks }: TaskFeedProps) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Task Feed</h2>
        <span className="text-sm text-ink/60">Priority queue</span>
      </div>
      <div className="overflow-hidden rounded-md border border-black/10 bg-white">
        {tasks.length > 0 ? (
          tasks.map((task) => (
            <div
              key={task.id}
              className="grid grid-cols-[1fr_auto_auto] items-center gap-4 border-b border-black/10 px-4 py-3 last:border-b-0"
            >
              <span className="min-w-0 truncate text-sm font-medium text-ink">
                {taskTitle(task)}
              </span>
              <span className="text-sm text-ink/60">{task.state}</span>
              <span className="w-10 text-right text-sm tabular-nums text-clay">
                {task.priority}
              </span>
            </div>
          ))
        ) : (
          <div className="px-4 py-3 text-sm text-ink/60">No tasks dispatched yet.</div>
        )}
      </div>
    </section>
  );
}
