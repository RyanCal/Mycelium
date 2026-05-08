'use client';

import { useEffect, useMemo, useState } from 'react';
import { fetchAgentCatalog, fetchAgents } from '@/lib/api';
import type { Agent, AgentCatalog } from '@/lib/types';

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function SettingsClient() {
  const [catalog, setCatalog] = useState<AgentCatalog>({});
  const [agents, setAgents] = useState<Agent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      try {
        const [nextCatalog, nextAgents] = await Promise.all([
          fetchAgentCatalog(),
          fetchAgents(),
        ]);
        if (!cancelled) {
          setCatalog(nextCatalog);
          setAgents(nextAgents);
          setError(null);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Unable to load settings');
          setLoading(false);
        }
      }
    }

    refresh();
    return () => {
      cancelled = true;
    };
  }, []);

  const spentByType = useMemo(() => {
    return agents.reduce<Record<string, number>>((totals, agent) => {
      totals[agent.type] = (totals[agent.type] ?? 0) + agent.tokens_used_today;
      return totals;
    }, {});
  }, [agents]);

  const rows = Object.entries(catalog).sort(([left], [right]) => left.localeCompare(right));

  return (
    <div className="mx-auto max-w-7xl px-5 py-6">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-ink">Settings</h1>
          <p className="mt-1 text-sm text-ink/65">Agent catalog</p>
        </div>
        <div className="rounded-md border border-black/10 bg-white px-3 py-2 text-sm text-ink/65">
          Read-only
        </div>
      </div>

      {error ? (
        <div className="mb-4 rounded-md border border-clay/40 bg-white px-4 py-3 text-sm text-clay">
          {error}
        </div>
      ) : null}

      <div className="overflow-hidden rounded-md border border-black/10 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead className="bg-mist text-xs font-semibold uppercase tracking-normal text-ink/65">
              <tr>
                <th className="px-4 py-3">Agent Type</th>
                <th className="px-4 py-3">Model</th>
                <th className="px-4 py-3">Daily Budget</th>
                <th className="px-4 py-3">Spent Today</th>
                <th className="px-4 py-3">Network</th>
                <th className="px-4 py-3">Enabled</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td className="px-4 py-4 text-ink/60" colSpan={6}>
                    Loading catalog...
                  </td>
                </tr>
              ) : null}
              {!loading && rows.length === 0 ? (
                <tr>
                  <td className="px-4 py-4 text-ink/60" colSpan={6}>
                    No agent types configured.
                  </td>
                </tr>
              ) : null}
              {rows.map(([agentType, entry]) => (
                <tr key={agentType} className="border-t border-black/10">
                  <td className="px-4 py-3">
                    <div className="font-medium text-ink">{agentType}</div>
                    <div className="mt-1 max-w-md text-xs leading-5 text-ink/60">
                      {entry.description}
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-ink/75">
                    {entry.default_model}
                  </td>
                  <td className="px-4 py-3 text-ink/75">
                    {formatNumber(entry.daily_token_budget)}
                  </td>
                  <td className="px-4 py-3 text-ink/75">
                    {formatNumber(spentByType[agentType] ?? 0)}
                  </td>
                  <td className="px-4 py-3 text-ink/75">
                    {entry.network_access ? 'Allowed' : 'Blocked'}
                  </td>
                  <td className="px-4 py-3">
                    <input
                      aria-label={`${agentType} enabled`}
                      checked={entry.enabled}
                      className="h-4 w-4 accent-moss"
                      disabled
                      readOnly
                      type="checkbox"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
