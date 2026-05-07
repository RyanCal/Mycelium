import type { StateCreator } from 'zustand';
import type { Agent } from '@/lib/types';

export type AgentsSlice = {
  agents: Agent[];
  setAgents: (agents: Agent[]) => void;
};

export const createAgentsSlice: StateCreator<AgentsSlice, [], [], AgentsSlice> = (set) => ({
  agents: [],
  setAgents: (agents) => set({ agents }),
});
