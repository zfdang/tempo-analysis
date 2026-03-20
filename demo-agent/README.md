# Conference Trip Agent Design Spec

## 1. Product Definition

This demo agent is a **chat-driven conference trip planning agent** built on top of Tempo.

It is not a general-purpose autonomous shopper.

Its job is very specific:

- read a natural-language travel request
- search flights and hotels
- apply explicit user constraints
- compare candidate itineraries
- pay for the search services using Tempo
- return a ranked trip plan with receipts and spend logs

## 2. Canonical User Request

The canonical request the agent is designed to handle is:

```text
Read https://tempo.xyz/SKILL.md and use it to find me hotels and a flight
to a conference in New York, Dec 28-29. No red-eyes, keep it under $700 total.
```

The first version of the agent must be able to handle requests of this shape reliably.

## 3. What The Agent Does and Does Not Do

### What it does

- parses a trip request from chat
- extracts structured constraints
- calls paid travel-search services
- pays those services with Tempo
- ranks the best flight + hotel combinations
- returns a recommendation and alternatives

### What it does not do in v1

- directly book airline inventory
- directly book hotel inventory
- settle payment to airlines or hotels
- manage cancellations or refunds

## 4. Important Assumption

As of **March 20, 2026**, Tempo's public docs and ecosystem materials describe agentic commerce as a target use case, including travel booking as a future example, but they do not list a clearly available Tempo-native hotel or flight booking merchant that this demo can depend on.

So this demo is designed as a **paid search and recommendation agent**, not a fully autonomous booking agent.

If a Tempo-native travel merchant appears later, the architecture below can be extended with a booking executor.

## 5. Demo Goal

The demo should prove one concrete thesis:

> An AI agent can use Tempo to pay for machine services in stablecoins, under bounded authority, to complete a real task with measurable business value.

For this demo, the real task is:

> produce a conference trip plan that satisfies travel constraints and budget constraints

## 6. User Experience

The user interacts with a chat interface.

### Example input

```text
Find me hotels and a flight to a conference in New York, Dec 28-29.
Depart from San Francisco. No red-eyes. Keep it under $700 total.
```

### Expected output shape

The agent returns:

1. one recommended itinerary
2. two backup options
3. a budget summary
4. an explanation of tradeoffs
5. the external search services used
6. Tempo payment receipts or transaction hashes for those service calls

### Example output

```text
Recommended plan
- Flight: SFO -> JFK, Dec 28 morning, return Dec 29 evening
- Hotel: 1 night near Midtown
- Estimated total: $642

Why this is best
- No red-eye
- Lowest total cost among options arriving before 3 PM
- Hotel is within 20 minutes of venue

Alternatives
- Option B: cheaper hotel, worse flight timing, total $618
- Option C: better hotel, slightly over preferred area, total $689

Search spend
- Flight search API: 0.18 pathUSD
- Hotel search API: 0.22 pathUSD
- Tx hashes: ...
```

## 7. Deterministic Functional Scope

The agent supports exactly one primary workflow in v1:

### Workflow

- user provides conference trip request
- agent extracts trip constraints
- agent queries flight search service
- agent queries hotel search service
- agent optionally queries mapping or commute-time service
- agent scores combinations
- agent returns ranked options

### Required constraints supported in v1

- destination city
- conference dates
- origin airport or city
- total budget cap
- red-eye allowed or disallowed
- hotel nights
- max distance to venue or target neighborhood
- hotel star range if provided

### Nice-to-have constraints

- preferred airlines
- preferred hotel chains
- baggage needs
- refundable-only preference
- arrival-before / departure-after time windows

## 8. Travel-Specific System Boundary

The agent is composed of two kinds of integrations:

### Tempo-native infrastructure

- Tempo account
- Tempo `0x76` transactions
- Tempo access key
- Tempo stablecoin fee payment
- MPP payment negotiation
- optional fee sponsorship

### Non-Tempo travel data services

- flight search API
- hotel search API
- optional venue distance / map API

The key design choice is:

> Tempo is the payment rail for machine services, not the travel inventory provider.

## 9. Required External Services

Because Tempo does not currently provide a known native hotel/flight merchant surface for this task, the demo must depend on **service wrappers** that expose travel search through a Tempo-payable interface.

### Required service 1: Flight Search Gateway

Responsibilities:

- accept structured flight search requests
- return candidate itineraries with times and prices
- expose pricing through MPP
- accept Tempo as a payment method

### Required service 2: Hotel Search Gateway

Responsibilities:

- accept structured hotel search requests
- return hotel options with nightly rates and location data
- expose pricing through MPP
- accept Tempo as a payment method

### Optional service 3: Commute or Maps Gateway

Responsibilities:

- calculate travel time from hotel to venue
- support filtering by distance or commute threshold
- expose pricing through MPP if used

## 10. Why MPP Matters Here

The travel search services should be treated as **paid machine services**.

The request flow is:

```text
search request -> 402 Payment Required -> Tempo payment -> retry -> search result
```

This is the cleanest way to show Tempo's value in the demo:

- the agent needs external data
- that data is monetized
- the agent pays automatically
- the result is returned in the same workflow

## 11. Tempo Account Model

The agent should use this account structure:

- **root key**: held by operator
- **runtime key**: Tempo access key
- **agent runtime**: signs only with the runtime key

### Recommended root key choice

- operator-controlled passkey or secure admin key

### Recommended runtime key choice

- dedicated `secp256k1` access key with strict token limits

This makes the demo safe enough to run repeatedly without exposing the root credential to the agent process.

## 12. Payment Policy

The runtime access key must have hard limits.

### Onchain limits

- short expiry such as 24 hours
- spending limit on `pathUSD`
- all other tokens disabled by default unless explicitly enabled

### Offchain policy limits

- max spend per search call
- max spend per end-user task
- allowlist of approved search services
- max swap size if conversion is needed

### Suggested demo defaults

- max search spend per task: `$2`
- max total service spend per day: `$25`
- max total travel plan budget accepted from user: `$1500`

The last number is not search spend. It is the user-facing trip budget cap for itinerary construction.

## 13. Supported Tempo Features

The demo must use Tempo in a way that is visible and meaningful.

### Required Tempo features

- **TIP-20 stablecoin payment**
- **Tempo `0x76` transaction type**
- **Access Key signing**
- **MPP payment flow**
- **stablecoin-denominated fees**

### Optional Tempo features

- fee sponsorship
- DEX swap before service payment
- separate nonce lanes per task

## 14. Main Runtime Components

```text
Chat UI
  |
  v
Trip Request Parser
  |
  v
Constraint Normalizer
  |
  +--> Flight Search Orchestrator
  +--> Hotel Search Orchestrator
  +--> Venue Distance Orchestrator
  |
  v
Itinerary Ranker
  |
  v
Response Generator

Shared Services:
- MPP Client
- Tempo Payment Engine
- Access Key Signer
- Policy Engine
- Audit Logger
```

## 15. Component Responsibilities

### 15.1 Chat UI

Responsible for:

- accepting natural-language requests
- displaying progress
- rendering ranked trip options

### 15.2 Trip Request Parser

Responsible for:

- extracting origin, destination, dates, budget, and preferences
- identifying missing required fields

### 15.3 Constraint Normalizer

Responsible for:

- converting user language into structured filters
- resolving date ranges
- normalizing airport and city names

### 15.4 Flight Search Orchestrator

Responsible for:

- building flight search queries
- calling one or more paid flight search gateways
- collecting results
- normalizing them into a shared schema

### 15.5 Hotel Search Orchestrator

Responsible for:

- building hotel search queries
- calling one or more paid hotel search gateways
- collecting results
- normalizing them into a shared schema

### 15.6 Venue Distance Orchestrator

Responsible for:

- estimating hotel-to-venue distance or commute
- filtering results that violate location constraints

### 15.7 Itinerary Ranker

Responsible for:

- generating valid flight + hotel combinations
- rejecting combinations over budget
- scoring remaining combinations

### 15.8 MPP Client

Responsible for:

- handling `402 Payment Required`
- parsing `WWW-Authenticate: Payment`
- choosing Tempo as the payment method
- retrying with `Authorization: Payment`

### 15.9 Tempo Payment Engine

Responsible for:

- building Tempo `0x76` transactions
- selecting fee token
- assigning nonce lanes
- applying `valid_before` to time-sensitive payments
- submitting transactions and collecting hashes

### 15.10 Policy Engine

Responsible for:

- service allowlist checks
- budget checks
- payment authorization checks
- escalation when a request exceeds policy

### 15.11 Audit Logger

Responsible for:

- storing task IDs
- storing search service calls
- storing MPP challenge IDs
- storing Tempo transaction hashes
- storing receipts and costs

## 16. Input Contract

The parser should emit a structured request object like this:

```json
{
  "trip_type": "conference",
  "origin": "SFO",
  "destination_city": "New York",
  "date_start": "2026-12-28",
  "date_end": "2026-12-29",
  "budget_total_usd": 700,
  "no_red_eye": true,
  "hotel_nights": 1,
  "venue_name": null,
  "preferred_area": null,
  "max_hotel_distance_minutes": null
}
```

### Required fields

- origin
- destination city
- trip date range
- total budget

### Clarification behavior

If any required field is missing, the agent asks one short clarification question before spending money on external search.

## 17. Output Contract

The response generator should emit three sections.

### Section 1: Recommended option

- chosen flight
- chosen hotel
- estimated total
- short explanation

### Section 2: Alternatives

- at least two alternatives when available
- explicit tradeoffs for each

### Section 3: Execution trace

- services queried
- cost to query each service
- Tempo tx hash or receipt ID for each paid call

## 18. Ranking Logic

The agent must not rank options arbitrarily.

### Hard filters

- over budget
- includes red-eye when user forbids it
- missing required hotel night count
- invalid date alignment
- hotel too far from venue if max distance is specified

### Scoring order

1. satisfies all hard constraints
2. lowest total cost
3. best arrival/departure timing
4. best venue proximity
5. best hotel quality within remaining budget

## 19. Payment Flow

For each paid search service call:

1. Runtime sends the search request.
2. Service returns `402 Payment Required`.
3. MPP client parses the challenge.
4. Policy engine checks service and spend limits.
5. Tempo payment engine builds a `0x76` transaction.
6. Runtime signs with the access key.
7. Transaction is submitted on Tempo.
8. MPP client retries with payment credentials.
9. Search result is returned.
10. Audit logger records tx hash, spend, and response metadata.

## 20. Use of Tempo `0x76`

The runtime should use Tempo `0x76` by default because it gives the demo several concrete advantages:

- stablecoin fee payment
- access-key signing
- optional fee sponsorship
- batched calls where needed
- time-bounded validity for machine-service payments

### Recommended defaults

- `fee_token`: `pathUSD`
- `nonce_key`: one lane per user task
- `valid_before`: now + 2 minutes for each service payment

## 21. State Machine

The agent runtime should move through these states:

```text
RECEIVED
-> PARSED
-> VALIDATED
-> FLIGHT_SEARCHING
-> HOTEL_SEARCHING
-> OPTION_SCORING
-> RESPONSE_READY
-> COMPLETED
```

### Failure states

- `NEEDS_CLARIFICATION`
- `SEARCH_BUDGET_EXCEEDED`
- `SERVICE_UNAVAILABLE`
- `PAYMENT_FAILED`
- `NO_VALID_ITINERARY`

## 22. Data Model

The runtime should persist these records.

### TripTask

- `task_id`
- `user_prompt`
- `normalized_request`
- `status`
- `budget_total_usd`

### ServiceCall

- `service_call_id`
- `task_id`
- `service_name`
- `service_type`
- `request_payload_hash`
- `status`

### PaymentAttempt

- `payment_attempt_id`
- `service_call_id`
- `mpp_challenge_id`
- `token`
- `amount`
- `fee_token`
- `tx_hash`
- `receipt_id`
- `status`

### RankedOption

- `task_id`
- `option_id`
- `flight_id`
- `hotel_id`
- `flight_cost`
- `hotel_cost`
- `estimated_total`
- `score`
- `rank`

## 23. Example Policy File

```yaml
account:
  default_fee_token: pathUSD
  sponsored_fees: true

runtime_key:
  expires_in_hours: 24
  token_limits:
    pathUSD: 25000000

task_policy:
  max_search_spend_usd: 2
  max_trip_budget_usd: 1500

services:
  flight-search-gateway:
    allow: true
    mpp_method: tempo
    max_amount_per_call: 500000

  hotel-search-gateway:
    allow: true
    mpp_method: tempo
    max_amount_per_call: 500000

  map-gateway:
    allow: true
    mpp_method: tempo
    max_amount_per_call: 200000
```

Values above are illustrative and assumed to be in token base units where relevant.

## 24. Demo Success Criteria

The demo is successful if a user can submit a request like:

```text
Find me hotels and a flight to a conference in New York, Dec 28-29.
Depart from SFO. No red-eyes. Keep it under $700 total.
```

And the system can reliably show:

1. the parsed constraints
2. the paid search service calls
3. the Tempo payments for those service calls
4. a ranked list of itineraries
5. one recommended option with reasoning

## 25. Non-Goals for This Demo

This demo is not trying to prove:

- end-to-end travel checkout on Tempo
- merchant acquisition on Tempo
- real airline or hotel settlement on Tempo
- decentralized travel booking markets

Those can be future demos, but they are not required to make this one compelling.

## 26. Future Extension

If a Tempo-native travel merchant or booking API becomes available, add a new component:

- **Booking Executor**

Responsibilities:

- confirm selected itinerary
- place booking hold or purchase
- return merchant confirmation ID
- handle booking-specific payment flow

Until then, the current agent ends at:

- search
- compare
- recommend
- hand off to human booking if needed

## 27. Short Summary

This demo agent should be understood as:

> a chat-based conference trip planner that uses Tempo to pay for travel-search services over MPP, under strict spending and authorization controls

That is concrete enough to build, constrained enough to demo well, and aligned with what Tempo can credibly support today.

## 28. Companion Files

This folder also includes implementation-oriented companion files:

- [architecture.md](architecture.md): system architecture, component boundaries, and request/payment flow
- [policy.example.yaml](policy.example.yaml): example runtime policy and budget configuration
- [request-schema.json](request-schema.json): structured request schema emitted by the parser
- [response-schema.json](response-schema.json): structured response schema returned by the agent
- [mvp-plan.md](mvp-plan.md): phased build plan for getting the demo into a runnable state
