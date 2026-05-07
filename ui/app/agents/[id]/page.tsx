export default async function AgentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="mx-auto max-w-5xl px-5 py-6">
      <h1 className="text-xl font-semibold text-ink">Agent {id}</h1>
      <p className="mt-2 text-sm text-ink/65">Agent detail view is scheduled for Phase 1.</p>
    </main>
  );
}
