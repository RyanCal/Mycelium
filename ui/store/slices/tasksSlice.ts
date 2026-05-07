import type { StateCreator } from 'zustand';
import type { Task } from '@/lib/types';

export type TasksSlice = {
  tasks: Task[];
  setTasks: (tasks: Task[]) => void;
};

export const createTasksSlice: StateCreator<TasksSlice, [], [], TasksSlice> = (set) => ({
  tasks: [],
  setTasks: (tasks) => set({ tasks }),
});
