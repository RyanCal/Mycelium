import { create } from 'zustand';
import { createAgentsSlice, type AgentsSlice } from './slices/agentsSlice';
import { createCommsSlice, type CommsSlice } from './slices/commsSlice';
import { createTasksSlice, type TasksSlice } from './slices/tasksSlice';

export type StoreState = AgentsSlice & TasksSlice & CommsSlice;

export const useStore = create<StoreState>()((...args) => ({
  ...createAgentsSlice(...args),
  ...createTasksSlice(...args),
  ...createCommsSlice(...args),
}));
