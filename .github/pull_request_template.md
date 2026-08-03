Task: <exact bead ID>
Author-Agent: <agent/tool ID>
Author-Family: <anthropic|deepseek|google|human|moonshot|openai|xai>
Risk: <tiny|substantial|protected>
Protected-Boundary: <none or exact boundary>
Deployment-Effect: <none or target and expected effect>

<!-- The task must match the claim and `<type>/<bead-id>-<slug>` branch exactly. Delivery
     automation is disabled while Mycelium is on hold. Models may raise risk but never lower a
     deterministic protected boundary. Protected work stops for authorization after full review. -->

## What

## Why

## Validation Evidence

- Tests / deterministic gates:
- Running smoke:
- Exact-Head-Review: <not required for tiny, or reviewer family + exact head SHA>

<!-- Independent review must bind to the current head. PR comments are informational and never
     authoritative controller, verdict, or merge state. -->

## Rollback

`<one command, or "not deployed" plus deterministic revert command>`

## Follow-Ups

None.
