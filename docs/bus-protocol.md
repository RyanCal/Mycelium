# Bus Protocol

Every Redis message is a `bus.envelope.Envelope`. The envelope metadata is
stable; `payload` is the flexible extension point.

Channels:

- `kernel.events`
- `kernel.commands`
- `agent.<agent_id>.inbox`
- `agent.<agent_id>.outbox`
- `agents.broadcast`
- `sandbox.<agent_id>.stdout`
- `sandbox.<agent_id>.results`
- `memory.invalidate`
- `experiments.<exp_id>.events`

Publishers write every envelope to `comms_log` before publishing to Redis.
