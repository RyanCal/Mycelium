import type { StateCreator } from 'zustand';

export type TaskSummary = {
  id: string;
  title: string;
  state: string;
  priority: number;
};

export type TasksSlice = {
  tasks: TaskSummary[];
  setTasks: (tasks: TaskSummary[]) => void;
};

export const createTasksSlice: StateCreator<TasksSlice, [], [], TasksSlice> = (set) => ({
  tasks: [],
  setTasks: (tasks) => set({ tasks }),
});
