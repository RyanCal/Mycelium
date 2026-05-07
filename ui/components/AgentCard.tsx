type AgentCardProps = {
  agent: {
    name: string;
    status: string;
    type: string;
    budget: string;
  };
};

export function AgentCard({ agent }: AgentCardProps) {
  return (
    <article className="rounded-md border border-black/10 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-ink">{agent.name}</h3>
          <p className="mt-1 text-sm text-ink/60">{agent.type}</p>
        </div>
        <span className="rounded-sm bg-mist px-2 py-1 text-xs font-medium text-moss">
          {agent.status}
        </span>
      </div>
      <div className="mt-4 text-sm text-ink/70">
        <span className="font-medium text-ink">Budget</span> {agent.budget}
      </div>
    </article>
  );
}
