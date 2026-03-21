# Proposals for Agent Passport

## Positioning

This document envisions an independent, generalized control plane for agent-commerce. We position this as a direct alternative to vertically integrated systems like Tempo. While Tempo tightly couples the agent runtime, the wallet, and the underlying infrastructure, our design decouples them, letting us act as a portable trust layer spanning any wallet or provider paradigm.

`x402` and `MPP` are treated strictly as interoperable transport protocols at the HTTP layer:

- `x402` handles discrete, pay-per-request transactions.
- `MPP` handles the richer framework for `charge`, time-bound `session`, and streaming-style interactions.

Our product differentiation comes directly from the passport platform:

- portable agent identity beyond a single platform
- bounded spending authority cryptographically assured
- merchant-readable stateless policy
- budget enforcement strictly enforced before money moves
- unified receipts and universal audit trails
- funding and settlement decoupled from a single chain or wallet model

## What "Agent Passport" Should Mean

An **Agent Passport** is a signed capability bundle that allows an agent to purchase services within strict policy boundaries.

At minimum, a passport should answer six questions:

1. Who is the human or organization behind the agent?
2. Which runtime key or agent instance is allowed to spend?
3. What budget is available?
4. Which merchants, tools, or SKUs are allowed?
5. Which payment protocols are allowed: `x402`, `MPP`, or both?
6. How are receipts, revocation, and disputes handled?

The key idea is:

> The passport is the product.
>
> Wallets, payment rails, and HTTP payment protocols are supporting infrastructure.

## Design Goals

- **Budget first**: the system must enforce spend limits before payment is submitted.
- **Protocol neutral**: one internal model should support both `x402` and `MPP`.
- **Merchant friendly**: merchants should be able to verify whether a passport is valid without deep custom integration.
- **Portable**: the same passport model should work across many services.
- **Revocable**: the operator must be able to stop spending immediately.
- **Auditable**: every charge, retry, receipt, and budget update must be traceable.
- **Composable**: the simple design should evolve into the medium and complex designs without rewriting the whole runtime.

## Threat Model

Any agent-commerce system must address these attack vectors. The three proposals differ in how completely they cover each one.

| Threat | Description | Mitigation |
| --- | --- | --- |
| Budget race condition | Two concurrent tool calls both check budget before either commits, leading to overspend | Reservation-based budget hold with atomic compare-and-reserve |
| Replay attack | A previously valid payment credential is resubmitted to obtain a second result | Challenge IDs must be single-use; receipts must be idempotent on challenge ID |
| Passport forgery | An attacker crafts a fake passport to spend against someone else's budget | Cryptographic signature verification on the passport; issuer key rotation |
| Key compromise | The agent runtime key is leaked | Short-lived passports; immediate revocation; `revocation_version` bump invalidates old keys |
| Merchant overcharge | A merchant claims a higher amount than originally quoted in the challenge | Budget guard compares reserved amount against challenge amount; commit rejects mismatches |
| Proxy compromise (Proposal A) | The central proxy is taken over | In Proposal A this is catastrophic. Proposal B and C reduce blast radius through decentralized verification |
| Phantom reservations | A reservation is never committed or released, permanently reducing available budget | Reservation TTL with auto-expiry prevents permanent phantom holds |
| Merchant denial-of-service | A merchant issues valid challenges but never delivers the service after payment | Receipts record delivery status; dispute flow needed in Proposal B/C |

## Shared Core Model

All three proposals should share the same logical objects, even if the implementation differs.

### 1. Passport

```json
{
  "schema_version": "1.0",
  "passport_id": "ap_01H...",
  "issuer": "passport.example",
  "subject": {
    "account_id": "org_123",
    "agent_id": "agent_researcher_7",
    "runtime_pubkey": "ed25519:...",
    "key_algorithm": "Ed25519"
  },
  "capabilities": {
    "protocols": ["x402", "mpp"],
    "intents": ["charge"],
    "allowed_merchants": ["api.flight.example", "api.hotel.example"],
    "allowed_skus": ["search.flight", "search.hotel"],
    "max_calls_per_minute": 30
  },
  "budget": {
    "currencies": ["USD"],
    "total_cap": "25.00",
    "per_call_cap": "2.00",
    "daily_cap": "10.00"
  },
  "validity": {
    "not_before": "2026-03-21T00:00:00Z",
    "not_after": "2026-03-22T00:00:00Z"
  },
  "revocation_version": 7,
  "issuer_signature": "base64url:..."
}
```

Key schema notes:

- `schema_version` enables backward-compatible evolution of the passport format.
- `issuer_signature` covers the entire passport body. Merchants and verifiers must check this before accepting.
- `key_algorithm` makes the signature scheme explicit, preventing algorithm confusion attacks.
- `currencies` is an array instead of a single value, to support multi-currency budgets in later phases.
- `max_calls_per_minute` provides rate-limiting independent of budget, preventing runaway loops even when budget is available.

### 2. Challenge Envelope

When a merchant returns `402 Payment Required`, the response carries protocol-specific challenge data. Both `x402` and `MPP` challenges should be normalized into one internal structure:

- `protocol` — `"x402"` or `"mpp"`
- `merchant` — the origin or merchant identifier
- `intent` — `"charge"`, `"session_open"`, etc.
- `challenge_id` — unique identifier from the merchant
- `request_binding` — hash or reference tying the challenge to the original request
- `amount` — quoted price
- `currency` — e.g. `"USD"`
- `payment_methods` — array of accepted methods (e.g. `["stablecoin", "card"]`)
- `expires_at` — challenge expiration timestamp

This normalization is critical because the budget guard, policy engine, and receipt store should never need to understand protocol-specific wire formats. Adding a new payment protocol in the future should only require writing a new adapter that maps into this envelope.

### 3. Budget Reservation

Before paying, the runtime should create a reservation with one of four states:

- `reserved` — amount is held against the budget
- `committed` — payment succeeded, amount is permanently deducted
- `released` — payment failed or was cancelled, hold is returned
- `expired` — reservation was not committed within its TTL and was auto-released

Every reservation should carry a short TTL (e.g. 30–120 seconds). If no commit or explicit release arrives within the TTL, the reservation expires automatically. This prevents phantom holds from permanently reducing available budget when a downstream call hangs or crashes.

This prevents concurrent tools from overspending the same passport budget.

### 4. Receipt Envelope

Every successful purchase should emit a canonical receipt:

- `passport_id`
- `merchant`
- `protocol`
- `challenge_id`
- `payment_id`
- `amount`
- `currency`
- `task_id`
- `timestamp`
- `verification_status`
- `delivery_status` — `succeeded`, `failed`, or `unknown`; tracks whether the merchant actually delivered the resource after payment

## Proposal A: Simple

### Name

**Local Passport + Central Payment Proxy**

### Summary

This is the fastest design to ship, acting as a viable MVP (Minimum Viable Product).

The passport is essentially a signed local policy document paired with a runtime key. The agent blindly routes all `x402` or `MPP` challenges to a central payment proxy controlled entirely by us. This proxy handles budget validation, executes the payment, handles retries, and records the receipt. The merchant remains oblivious to the passport, dealing only with our proxy.

### Core Idea

- keep the passport natively on the operator side
- keep merchant integration minimal (they only see standard API interactions)
- support only immediate one-shot purchases at first
- treat `MPP session` as entirely out of scope for this tier

### Main Components

- **Passport Issuer**
  - Creates a signed passport document.
- **Agent Runtime**
  - Holds the runtime key and the active passport.
- **Budget Guard**
  - Checks total cap, per-call cap, and merchant allowlist.
- **Payment Proxy**
  - Receives the 402 challenge, chooses the payment method, pays, retries, and returns the result.
- **Receipt Store**
  - Stores normalized receipts and spend logs.

### Flow

1. Operator creates a passport for one agent and one budget window.
2. Agent requests a paid resource.
3. Merchant returns `402 Payment Required` using either `x402` or `MPP`.
4. Agent forwards the challenge to our payment proxy.
5. Budget Guard verifies:
   - passport validity
   - merchant allowlist
   - per-call cap
   - remaining total budget
6. Budget Guard creates a reservation.
7. Payment Proxy fulfills the payment and retries the request.
8. On success, the reservation is committed and a receipt is stored.
9. On failure, the reservation is released.

### Budget Model

Three simple controls are enough for v1:

- total budget per passport
- max amount per call
- merchant allowlist

All budget state can live in one central database.

### Protocol Support

- `x402`: fully supported for one-shot paid calls
- `MPP charge`: supported through the same normalize -> reserve -> pay -> retry path
- `MPP session`: not supported

### Security Model

- runtime key is scoped to one passport
- passports are short-lived
- all spend is mediated by our proxy
- operators can revoke a passport centrally

### Key API Surface

The Proposal A system requires a small set of internal APIs. These do not need to be public at this stage.

```
POST   /passports                     # create a new passport
GET    /passports/{id}                # retrieve passport details
DELETE /passports/{id}                # revoke a passport

POST   /payments/challenge            # agent submits a 402 challenge
       → Budget Guard checks policy
       → Payment Proxy fulfills payment
       → returns result + receipt

GET    /budgets/{passport_id}         # current budget utilization
GET    /receipts?passport_id=...      # list receipts for a passport
```

This is intentionally minimal. The payment proxy is the only component that touches external payment rails.

### Advantages

- very fast to implement
- low merchant integration cost
- easy to observe and debug
- good fit for internal agents or early pilots

### Limitations

- passport is not truly portable across merchants
- merchants trust our proxy, not the passport directly
- central proxy is a single point of failure and a latency bottleneck at scale
- no real session model
- limited differentiation if we want to compete at platform level
- if the proxy is compromised, all passports are effectively compromised

### Best Fit

- internal copilots
- early design partners
- low-volume paid tools
- proving the user value of budgeted agent purchases

## Proposal B: Medium

### Name

**Signed Passport + Budget Ledger + Merchant Verifier**

### Summary

This is the core recommended architecture and the best productizable design for a scalable, independent platform.

The passport becomes a first-class, portable signed credential that merchants or gateways verify directly using a stateless SDK. We decouple from the underlying payment network by introducing a real budget ledger with robust reserve/commit semantics, a revocation mechanism, and a unified verification SDK supporting both `x402` and `MPP` smoothly without a centralized latency-inducing proxy bottleneck.

### Core Idea

- make the passport portable
- keep budget enforcement in our system
- let merchants verify the passport without trusting a hidden proxy
- keep payment methods and settlement rail-agnostic

### Main Components

- **Passport Authority**
  - Issues signed passports.
  - Rotates issuer keys.
  - Publishes revocation state.
- **Budget Ledger**
  - Tracks `available`, `reserved`, and `committed` balances.
  - Supports idempotent reservation.
- **Policy Engine**
  - Evaluates merchant, SKU, protocol, amount, time window, and task policy.
- **Payment Adapter Layer**
  - `x402 Adapter`
  - `MPP Adapter`
  - both normalize into the same internal challenge model
- **Merchant Verifier SDK**
  - Verifies passport signature
  - checks expiration and revocation
  - optionally checks budget authorization token
- **Receipt and Audit Service**
  - Stores canonical receipts
  - exposes operator dashboards and exports

### Flow

1. Operator or user creates a task budget.
2. Passport Authority issues a signed passport for the agent runtime.
3. Agent requests a paid tool or API.
4. Merchant returns an `x402` or `MPP` challenge.
5. Agent sends the challenge plus the passport to the Policy Engine.
6. Policy Engine asks Budget Ledger to reserve the quoted amount.
7. If approved, the system generates a short-lived **budget authorization token** (a compact JWT or similar signed structure) bound to:
   - passport ID
   - merchant origin
   - challenge ID
   - max spend amount and currency
   - expiration (typically 30–60 seconds)

   The token is signed by the Budget Ledger's key, not the passport issuer's key. This means merchants can verify spend authority without needing to track passport budget state themselves.

   Example decoded claims:
   ```json
   {
     "iss": "budget.passport.example",
     "sub": "ap_01H...",
     "merchant": "api.flight.example",
     "challenge_id": "ch_abc123",
     "max_amount": "2.00",
     "currency": "USD",
     "exp": 1742601660
   }
   ```
8. Payment Adapter executes the payment and retries the request.
9. Merchant verifies:
   - passport validity
   - budget authorization token
   - challenge binding
10. On success, the reservation is committed and a receipt is written.
11. On failure or timeout, the reservation is released.

### Budget Model

This design should support at least five policy dimensions:

- total passport budget
- per-call budget
- per-merchant daily budget
- per-task budget
- protocol and intent allowlist

This is where we become meaningfully better than a wallet-only or chain-only design:

- the budget model is service-aware
- budget decisions happen before settlement
- the same policy works across multiple payment rails
- multi-currency budgets are supported: a single passport can carry caps in USD, EUR, and other currencies, with the budget ledger tracking each independently

### Protocol Support

- `x402`: Fully supported as a single-step HTTP interaction verified synchronously by the stateless SDK.
- `MPP charge`: Fully supported, mapping smoothly to our internal reserve/commit ledger pipeline.
- `MPP session`: Partially supported as a controlled extension to provide immediate utility without massive overhead.

For `MPP session`, the Medium design specifically provides:

- An explicit session open request that locks the `session max budget` inside the ledger.
- A hard time-bound `session expiration` TTL.
- No requirement yet for the overhead of off-chain cryptographic voucher settlement (this is deferred to the Complex proposal).

### Settlement Strategy

Settlement should be abstracted behind a `Funding Backend` interface:

- internal prepaid balance
- stablecoin wallet
- card-on-file or processor-backed rail
- enterprise invoice account

This is important if we want to compete with a chain-centric model. The passport should survive even if the funding backend changes.

### Security Model

- signed passports with key rotation
- revocation endpoint or revocation list (CRL-style, polled or pushed)
- challenge-bound spend authorization tokens (JWT signed by Budget Ledger key)
- ledger-backed reservations with TTL-based auto-expiry
- idempotent payment and receipt handling
- all tokens have short lifetimes to reduce window of compromise
- passport and authorization token use separate signing keys to limit blast radius

### Advantages

- real passport portability
- stronger merchant trust model
- much better budget safety under concurrency
- clear differentiation as an agent-commerce platform
- can support both crypto-native and non-crypto rails

### Limitations

- more moving parts
- merchants need a verifier SDK or gateway support
- budget ledger becomes business-critical infrastructure
- `MPP session` support is still limited compared with a full network design

### Best Fit

- production SaaS agent platform
- multi-merchant ecosystems
- enterprise copilots with delegated budgets
- systems where auditability and revocation matter

## Proposal C: Complex

### Name

**Open Passport Network with Sessions, Escrow, and Delegated Sub-Budgets**

### Summary

This represents the ultimate end-state: a fully open, internet-native trust ecosystem that confidently competes with or subsumes heavily-integrated networks.

The passport is a universal, verifiable credential that any merchant can trust directly. It natively supports organizational tree structures via delegated sub-budgets and powers advanced `MPP session` lifecycles via incremental cryptographic vouchers. The platform abstracts away the final settlement rail entirely, dynamically routing across any funding source. It ceases to be a single payment helper and becomes the definitive authorization protocol for autonomous agent commerce.

### Core Idea

- passport is a portable network credential
- merchants can trust the passport directly
- budgets can be split, delegated, and re-scoped
- `x402` handles discrete purchases
- `MPP` handles sessions and high-frequency usage

### Main Components

- **Passport Trust Registry**
  - Publishes issuer keys
  - revocation feeds
  - merchant trust metadata
- **Passport Authority**
  - Issues root passports
  - delegates child passports or sub-budgets
- **Budget Vault**
  - Escrows or earmarks spendable funds
  - enforces hard budget ceilings
- **Risk Engine**
  - detects abnormal merchant behavior
  - throttles or freezes passports in real time
- **Session Controller**
  - opens, meters, and settles `MPP session` usage
  - tracks session lifecycle: `open` → `active` → `settling` → `closed`
  - enforces per-session budget envelope
- **Voucher Engine**
  - signs incremental spend claims for session-based billing
  - each voucher is a compact signed message: `(session_id, sequence, cumulative_amount, timestamp, signature)`
  - vouchers are monotonically increasing in `cumulative_amount`, so the merchant only needs to verify the latest one
  - settlement reconciles the final voucher against the session budget
- **Payment Router**
  - chooses funding source and settlement rail
- **Merchant Verifier SDK / Gateway**
  - validates passport, session state, vouchers, and receipts
- **Global Receipt Graph**
  - links sessions, charges, sub-budgets, and merchant outcomes

### Flow

1. Organization creates a root passport with a global budget.
2. The root passport delegates sub-passports to specific agents or tasks.
3. Each sub-passport contains:
   - its own cap
   - merchant scope
   - protocol scope
   - task scope
   - time window
4. Agent discovers a merchant and negotiates either:
   - `x402` one-shot purchase
   - `MPP charge`
   - `MPP session`
5. Budget Vault checks hard limits.
6. Risk Engine checks soft limits and merchant risk signals.
7. Payment Router chooses the rail.
8. If the purchase is one-shot, the system pays and commits a receipt.
9. If the purchase is session-based, the Session Controller opens a session and the Voucher Engine issues bounded incremental spend claims.
10. Merchant verifies the passport chain, voucher validity, and session headroom.
11. Settlement happens periodically, while receipts remain continuously visible to the operator.

### Budget Model

This design supports:

- hard escrowed budget
- soft policy budget
- per-agent sub-budgets
- per-task sub-budgets
- merchant risk tiers
- dynamic budget reallocation
- session budget envelopes
- real-time freeze or rollback windows

### Protocol Support

- `x402`: full network-verified trust architecture for discrete purchases.
- `MPP charge`: securely managed and ledger-guaranteed.
- `MPP session`: full escrow-backed voucher-streaming lifecycle.
- future streaming or metered protocols: pluggable natively through the Voucher Engine.

### Competitive Differentiation

This is where we stop looking like "another payment adapter" and start looking like a platform:

- identity-first, not chain-first
- budget and policy are first-class objects
- merchants verify spend authority directly
- supports both immediate purchase and long-running agent work
- funding can come from many rails without changing the passport abstraction

### Security Model

- verifiable credential chain from issuer to sub-passport
- revocation and freeze at every level
- escrow or reserve-backed spending guarantees
- challenge and voucher binding
- anomaly detection and adaptive risk controls

### Advantages

- strongest platform story
- best fit for broad merchant ecosystem adoption
- handles high-frequency and session-based usage well
- supports enterprise delegation and marketplace models
- hardest to copy once established

### Limitations

- by far the highest complexity
- requires merchant SDK adoption or gateway partnerships
- operational burden is much larger
- dispute handling and session settlement add product and legal complexity

### Best Fit

- open agent marketplaces
- infrastructure platforms
- external developer ecosystems
- internet-scale merchant networks

## Error Handling and Dispute Model

Payment failures and merchant disputes are inevitable. The system should define clear behavior for each case.

### Payment Failures

| Failure | System Behavior |
| --- | --- |
| Challenge expired before payment submitted | Release reservation, return error to agent, agent may retry the original request |
| Payment method rejected (insufficient funds, rail error) | Release reservation, return structured error with failure reason |
| Merchant unreachable during retry | Release reservation, return network error |
| Payment succeeded but merchant returned non-200 after retry | Commit the reservation (money moved), store receipt with `delivery_status: failed`, flag for dispute |
| Duplicate challenge ID detected | Reject as replay, do not reserve |

### Dispute Flow

In Proposal A, dispute handling is manual: the operator reviews receipts and contacts the merchant directly.

In Proposal B, the system should support a lightweight dispute lifecycle:

1. An agent or operator flags a receipt as disputed.
2. The system records the dispute with evidence (receipt, original challenge, delivery status).
3. Settlement for the disputed amount is held pending resolution.
4. Resolution is recorded and budget is adjusted if a refund is granted.

In Proposal C, disputes can be partially automated through the Risk Engine and session-level evidence.

## Privacy Considerations

The passport design should minimize data exposure at each layer.

- **Merchant visibility**: merchants should see the passport ID, issuer, validity window, and the budget authorization token. They should **not** see the total budget, daily budget, or the full list of other allowed merchants.
- **Data retention**: receipts should be retained for audit purposes. Raw payment credentials (signed payloads, card tokens) should not be stored longer than needed for settlement.
- **Agent isolation**: if an operator runs multiple agents, one agent's passport must not reveal the identity or budget of another agent.
- **Minimal claims in authorization tokens**: the budget authorization token should contain only the claims the merchant needs to verify. Do not embed operator identity, full budget state, or internal account details.

## Comparison Table

| Dimension | Proposal A | Proposal B | Proposal C |
| --- | --- | --- | --- |
| Time to ship | Fast | Medium | Slow |
| Passport portability | Low | Medium to High | Very High |
| Merchant verification | Proxy-based | SDK/gateway-based | Native network trust |
| Budget sophistication | Basic | Strong | Very Strong |
| `x402` support | Full | Full | Full |
| `MPP charge` support | Full | Full | Full |
| `MPP session` support | None | Limited | Full |
| Funding rails | Usually one | Multiple | Many, routed dynamically |
| Operational complexity | Low | Medium | High |
| Competitive strength | Low to Medium | High | Very High |

## Recommended Path

If the goal is to build a credible independent competitor, the best path is:

1. **Ship Proposal A as a bootstrap implementation** to prove demand and iterate on the passport schema.
2. **Ship Proposal B as the product direction** once the core abstractions are validated.
3. **Keep Proposal C as the long-term architecture** for ecosystem-scale ambition.

### Transition Criteria

Move from A to B when:

- at least 3 external merchants are integrated
- budget enforcement has been tested under concurrent agent workloads
- the passport schema has stabilized after real-world iteration
- operators are requesting features that require merchant-side verification (portability, multi-merchant tasks)

Move from B to C when:

- session-based billing is a top merchant request
- delegated sub-budgets are needed for multi-team or marketplace use cases
- the merchant verification SDK has meaningful adoption
- the system needs to support more than one settlement rail simultaneously

The reasoning is simple:

- Proposal A is good for proving demand, but too centralized and too thin to become a durable platform.
- Proposal C is strategically strong, but too expensive and risky to start with.
- Proposal B is the sweet spot where the passport becomes real, merchants can verify it, budgets are properly enforced, and both `x402` and `MPP` can be supported without tying the company to one settlement layer.

## Suggested Build Order

### Phase 1

- define the canonical passport schema
- define the normalized challenge schema for `x402` and `MPP`
- implement Budget Ledger with `reserve`, `commit`, and `release`
- implement signed passport issuance and revocation
- support `x402` and `MPP charge`

### Phase 2

- ship Merchant Verifier SDK
- add budget authorization tokens
- add merchant and SKU policy controls
- add multiple funding backends
- add operator dashboard and receipt exports

### Phase 3

- add session envelopes for `MPP`
- add delegated sub-budgets
- add risk engine
- add voucher-based session settlement
- add trust registry for broader ecosystem adoption

## Final Recommendation

The most defensible and independently disruptive design is:

> **An open, passport-centric platform where identity, budget, and merchant-readable authorization are first-class cryptographic objects, while `x402` and `MPP` are stripped down to act strictly as the transport protocols executing the purchases.**

This architectural framing establishes a commanding strategic counter-position:

- We are not "another closed-loop runtime."
- We are not "just another integrated wallet."
- We are not "just a centralized 402 proxy."

Instead, we are the foundational, interoperable control plane for budgeted agent commerce worldwide.
