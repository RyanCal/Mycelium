import type { StateCreator } from 'zustand';

export type CommsEvent = {
  id: string;
  channel: string;
  messageType: string;
  payload: Record<string, unknown>;
};

export type CommsSlice = {
  comms: CommsEvent[];
  pushComms: (event: CommsEvent) => void;
};

export const createCommsSlice: StateCreator<CommsSlice, [], [], CommsSlice> = (set) => ({
  comms: [],
  pushComms: (event) => set((state) => ({ comms: [event, ...state.comms].slice(0, 100) })),
});
