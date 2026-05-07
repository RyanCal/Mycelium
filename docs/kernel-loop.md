# Kernel Loop

`Kernel.start_daemon()` starts three loops:

- Tick loop: asks the scheduler for queued work and dispatches jobs to Arq.
- Bus loop: watches kernel commands, kernel events, and sandbox results.
- Heartbeat loop: marks busy agents errored when their heartbeat goes stale.

Each DB operation uses a short-lived async session. The kernel never holds a
long-lived session across ticks.
