import { ThoughtBubble } from '@/components/ThoughtBubble';

const events = [
  { source: 'kernel.events', body: 'agent.registered echo-default' },
  { source: 'kernel.events', body: 'scheduler waiting for queued work' },
  { source: 'sandbox.results', body: 'Phase 2 execution stream placeholder' },
];

export function CommsStream() {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Comms</h2>
        <span className="text-sm text-ink/60">Live tail in Phase 2</span>
      </div>
      <div className="rounded-md border border-black/10 bg-white p-4 shadow-sm">
        <div className="space-y-3">
          {events.map((event) => (
            <ThoughtBubble key={`${event.source}-${event.body}`} source={event.source} body={event.body} />
          ))}
        </div>
      </div>
    </section>
  );
}
