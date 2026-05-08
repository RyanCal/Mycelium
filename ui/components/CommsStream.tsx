export function CommsStream() {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-normal text-ink/65">Comms</h2>
        <span className="text-sm text-ink/60">Live tail in Phase 2</span>
      </div>
      <div className="rounded-md border border-black/10 bg-white p-4 shadow-sm">
        <div className="rounded-md border border-dashed border-black/15 bg-mist p-4">
          <div className="text-sm font-semibold text-ink">Phase 2 comms feed</div>
          <p className="mt-2 text-sm leading-6 text-ink/65">
            Live agent replies will appear here when the bus reply tracker is wired into the
            dashboard stream.
          </p>
        </div>
      </div>
    </section>
  );
}
