# Architecture

Mycelium is organized around four durable boundaries:

- Kernel: schedules tasks, owns lifecycle, enforces budgets, and exposes the API.
- Agents: perform domain work through a small `run_step` contract.
- Bus: carries typed envelopes over Redis Pub/Sub and persists every envelope.
- Memory/sandbox: stores recall and isolates execution.

The kernel and API run in one process to avoid a redundant IPC hop. Arq workers
run separately so slow agent work cannot block scheduler ticks.
