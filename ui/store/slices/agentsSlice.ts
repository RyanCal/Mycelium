import type { StateCreator } from 'zustand';

export type AgentSummary = {
  id: string;
  name: string;
  status: string;
  type: string;
};

export type AgentsSlice = {
  agents: AgentSummary[];
  setAgents: (agents: AgentSummary[]) => void;
};

export const createAgentsSlice: StateCreator<AgentsSlice, [], [], AgentsSlice> = (set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
});
