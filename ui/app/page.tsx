import { DashboardClient } from '@/components/DashboardClient';

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

      <DashboardClient />
    </main>
  );
}
