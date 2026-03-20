# Conference Trip Agent MVP Plan

## Goal

Ship a demo that can:

- accept a conference trip request in chat
- pay for flight and hotel search services with Tempo
- return ranked itinerary options

The MVP is successful when it demonstrates a complete:

```text
chat request -> paid machine service calls -> Tempo payment -> ranked trip plan
```

## Phase 1: Narrow Happy Path

Target:

- one origin city
- one destination city
- one flight search provider
- one hotel search provider
- no booking execution

Deliverables:

- chat input form
- parser for destination, dates, and budget
- mock or wrapped paid search services
- Tempo account and access key setup
- MPP payment flow
- simple ranked response

Exit criteria:

- one trip request completes end-to-end with visible Tempo tx hashes

## Phase 2: Realistic Constraints

Target:

- support `no red-eye`
- support hotel night count
- support venue distance filtering
- support fallback or alternative options

Deliverables:

- better constraint normalizer
- maps or commute enrichment
- harder ranking logic
- better error handling

Exit criteria:

- canonical sample prompt produces one recommendation and at least two alternatives when data exists

## Phase 3: Operator Controls

Target:

- stronger safety and observability

Deliverables:

- policy file loading
- budget enforcement
- service allowlists
- audit log viewer
- payment trace in UI

Exit criteria:

- operator can explain exactly what the agent spent, where, and why

## Phase 4: Demo Polish

Target:

- make it easy to show in a live demo

Deliverables:

- progress states in UI
- friendly result rendering
- summary card for recommended plan
- raw JSON trace view for technical demos

Exit criteria:

- the demo is understandable to both product and protocol audiences

## Suggested Repository Additions

When implementation begins, add:

- `demo-agent/app/` for chat UI
- `demo-agent/runtime/` for orchestration logic
- `demo-agent/integrations/` for search gateway clients
- `demo-agent/policies/` for environment-specific configs
- `demo-agent/examples/` for sample prompts and outputs

## First Build Checklist

- create Tempo-funded demo account
- authorize runtime access key
- implement `ConferenceTripRequest` validation
- implement one paid flight search call
- implement one paid hotel search call
- log payment tx hashes
- render ranked result

## Hard Rule

Do not add booking execution before the search-and-rank flow is stable.

For this demo, search and paid service orchestration are the proof point. Booking can come later.
