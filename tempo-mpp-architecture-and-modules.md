# Machine Payments Protocol (MPP): Architecture, Modules, and Internal Design

## Overview

The **Machine Payments Protocol (MPP)** is an open, internet-native protocol for **machine-to-machine payments**. At a high level, it extends the familiar HTTP request cycle so that payment can become part of the request itself:

**request → payment required → authorize → retry → response**

MPP was introduced by Tempo and Stripe as an open standard for programmatic payments and is designed to work across multiple payment rails, including stablecoins on Tempo, Stripe-backed fiat methods, Lightning, and custom methods.

A concise way to think about MPP is:

> **MPP is not just a billing convention.**
>
> **It is a protocol stack for requesting, authorizing, verifying, and settling payments inside ordinary service calls.**

---

## What MPP Standardizes

At the protocol level, MPP standardizes the shape of a paid request/response cycle:

- the server can challenge the client for payment using **HTTP 402**
- the challenge is carried in a **`WWW-Authenticate: Payment`** header
- the client answers with an **`Authorization: Payment`** header containing a payment credential
- the server verifies payment and returns the resource with a **`Payment-Receipt`** header

This gives agents, applications, and services a common way to conduct paid interactions inside one HTTP request flow rather than through a separate checkout or manual payment process.

MPP is also **payment-method agnostic**. A single endpoint can expose multiple supported methods and let the client choose the one it can fulfill.

---

## The Clean Mental Model

The best mental model is:

- **HTTP provides the transport**
- **MPP provides the payment handshake**
- **payment methods provide rail-specific settlement**
- **payment intents provide execution semantics**
- **SDKs provide developer ergonomics**
- **sessions provide high-frequency, low-cost continuous payment flows**

That is why MPP is best understood as a **layered protocol**, not just a single API helper.

---

## The Main Modules of MPP

MPP is not always documented as a formal "box-and-arrow module list," but based on the official docs, SDKs, and payment specifications, the architecture naturally decomposes into the following modules.

## 1. Transport and Authentication Module

This is the core protocol envelope.

It defines how payment requirements and payment proofs move through standard request/response flows. The key elements are:

- **`402 Payment Required`** as the payment challenge status
- **`WWW-Authenticate: Payment`** for the challenge
- **`Authorization: Payment`** for the payment credential
- **`Payment-Receipt`** for the settlement/result metadata

This module is what makes MPP feel like a native extension of HTTP rather than a separate payment RPC system.

### What this module is responsible for

- carrying payment requirements
- carrying payment credentials
- framing the retry flow
- keeping the interaction compatible with ordinary web infrastructure

---

## 2. Challenge Module

The challenge module is the server-side component that expresses **what payment is being requested**.

A challenge includes the key inputs a client needs to complete payment, including:

- the **payment method**
- the **payment intent**
- the **request** object (method-specific details)
- identifiers and bindings used to tie the challenge to a specific request

The underlying Payment HTTP Authentication scheme defines required challenge parameters such as:

- `id`
- `realm`
- `method`
- `intent`
- `request`

In practical deployments, the challenge also carries constraints such as:

- expiration
- request binding
- idempotency-related safety constraints
- pricing details such as amount, currency, or recipient information

### Why this module matters

Without a challenge module, every service would invent its own custom payment envelope. MPP standardizes this so clients can respond consistently across services.

---

## 3. Credential Module

The credential module is the client-side answer to the server challenge.

Once the client has chosen a supported method and fulfilled the payment requirement, it constructs a **payment credential** and retries the request.

The credential contains:

- the challenge reference
- payment-method-specific proof or authorization payload
- any required signatures or method-specific data

This module is responsible for turning "I know how to pay" into "here is a standardized proof that I paid or authorized payment."

### Examples by payment method

- **Tempo**: sign and submit the Tempo payment flow, then present the payment credential
- **Stripe / SPT**: create a Stripe-backed payment token and present it as the credential payload
- **Lightning**: present payment proof associated with the invoice flow
- **Custom**: follow the registered method specification

---

## 4. Payment Method Module

MPP supports multiple **payment methods** behind the same protocol envelope.

Public documentation identifies at least these methods:

- **Tempo**
- **Stripe**
- **Lightning**
- **Card**
- **Custom**

Each payment method defines its own method-specific request and payload structure while fitting into the same challenge/credential flow.

### What this module does

- defines rail-specific settlement details
- defines method-specific challenge data
- defines method-specific credential payloads
- allows one service to offer multiple rails simultaneously

This is one of MPP's biggest differences from simpler machine-payment flows: the transport is standardized, but the rail remains pluggable.

---

## 5. Payment Intent Module

MPP defines **payment intents** separately from payment methods.

This is a very important part of the architecture.

A **method** tells you *how value moves*.
An **intent** tells you *what kind of payment interaction is being requested*.

Public documentation currently identifies two main intents:

- **`charge`** — one-time payment that settles immediately
- **`session`** — streaming payment over a payment channel for metered or pay-as-you-go usage

This separation is elegant because it means the protocol can evolve without hardwiring every use case into one payment flow.

### Why intents are important

The same service may want very different execution models:

- "Pay once for this API call"
- "Open a session and pay continuously as tokens stream"
- "Charge per inference chunk"
- "Charge per request but support multiple rails"

By separating intent from method, MPP becomes a general machine-payments framework rather than a fixed per-request crypto protocol.

---

## 6. Verification and Settlement Module

Once the server receives a payment credential, it needs to verify that the payment is valid and settle or finalize the payment according to the selected method.

This module is responsible for:

- validating the challenge/credential relationship
- verifying signatures or payment proofs
- confirming the payment is valid for the requested method and intent
- executing or finalizing settlement where needed
- rejecting invalid, expired, replayed, or mismatched credentials

For a Tempo method, this might mean verifying the Tempo payment data and settlement conditions.
For a Stripe-backed method, this might mean consuming and processing a Shared Payment Token.
For Lightning, it means verifying Lightning payment proof.

### Why this module matters

MPP would not be production-ready if it only defined how to ask for payment.
It also needs a standardized way to answer: **"Was this payment valid for this exact request?"**

---

## 7. Receipt Module

After successful verification and settlement, the server returns the protected resource and includes a **receipt**.

The receipt is a protocol object, not just an application-specific log line. It gives the interaction a standard post-payment artifact that can be used for:

- confirmation
- auditability
- downstream accounting
- programmatic tracing
- proof that access was granted after payment

This module completes the flow by making the payment outcome machine-readable.

---

## 8. Session Module

The **session** module is the biggest architectural expansion beyond basic pay-per-request flows.

Sessions are designed for:

- streaming services
- metered usage
- high-frequency, low-value requests
- continuous agent-service interaction
- sub-cent or near-real-time billing

Public descriptions of MPP sessions explain the model like this:

- the client **locks or sets aside funds upfront**
- the client then issues **signed vouchers offchain**
- the server consumes resources incrementally
- settlement happens **periodically** rather than requiring a separate onchain or full payment round-trip for every tiny interaction

Tempo describes this as "OAuth for money": authorize once, then allow bounded, programmatic payment execution within defined limits.

### Why the session module matters

Without sessions, machine payments remain too expensive or too slow for many internet-native use cases such as:

- token-by-token model generation
- streamed inference
- continuous data feeds
- usage-metered compute
- dense multi-service agent workflows

Sessions turn MPP from a "paywall for one request" into a broader infrastructure layer for agentic commerce.

---

## 9. Discovery Module (Optional but Important)

MPP's broader specification set also includes **service discovery** based on OpenAPI.

The discovery layer lets services publish machine-readable payment metadata such as:

- service categories
- documentation links
- payment-enabled operations
- per-operation payment metadata through `x-payment-info`

This is not required for runtime payments, because the runtime **402 challenge remains authoritative**, but it improves the developer and agent experience by making payable services discoverable ahead of time.

### Why discovery matters

This is the bridge from:
- "a paid endpoint exists"
to
- "an agent can discover, understand, and invoke that paid endpoint automatically"

So discovery is not the payment path itself, but it is part of the broader MPP ecosystem design.

---

## 10. SDK and Middleware Module

MPP is designed to be used through SDKs and middleware, not only by hand-crafting headers.

Publicly documented SDKs include:

- **TypeScript** — `mppx`
- **Python** — `pympp`
- **Rust** — `mpp-rs`

The TypeScript SDK also includes middleware or integrations for frameworks such as:

- Hono
- Express
- Next.js
- Elysia

SDKs handle tasks such as:

- parsing 402 payment challenges
- selecting methods
- creating credentials
- retrying requests
- returning receipts
- offering CLI tools for testing and local development

This is the developer-runtime module of MPP.

---

## A Practical Architecture Diagram

Below is a practical, engineering-oriented diagram of MPP's architecture.

```text
┌──────────────────────────────────────────────────────────────────┐
│                        Application Layer                         │
│                                                                  │
│   Agents / apps / SDK users call paid APIs, tools, or content    │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    MPP Client Runtime Module                     │
│                                                                  │
│  - fetch wrapper / middleware / SDK                              │
│  - parses payment challenges                                     │
│  - selects payment method + intent                               │
│  - creates payment credentials                                   │
│  - retries requests automatically                                │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│               HTTP Payment Transport / Auth Module               │
│                                                                  │
│  Request → 402 + WWW-Authenticate: Payment                       │
│  Retry   → Authorization: Payment                                │
│  Success → Payment-Receipt + resource                            │
└──────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌─────────────────────────────┐   ┌───────────────────────────────┐
│       Challenge Module      │   │      Credential Module        │
│                             │   │                               │
│  - id / realm               │   │  - challenge reference        │
│  - method                   │   │  - method-specific proof      │
│  - intent                   │   │  - authorization payload      │
│  - request details          │   │  - signatures / tokens        │
│  - binding / expiry         │   │                               │
└─────────────────────────────┘   └───────────────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│              Verification + Settlement Module                    │
│                                                                  │
│  - verify credential against challenge                           │
│  - execute or finalize rail-specific settlement                  │
│  - reject replay / expiry / mismatch                             │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                 Method + Intent Abstraction Layer                │
│                                                                  │
│  Methods: Tempo | Stripe | Lightning | Card | Custom            │
│  Intents: charge | session                                       │
└──────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌─────────────────────────────┐   ┌───────────────────────────────┐
│        Charge Engine        │   │         Session Engine        │
│                             │   │                               │
│  one-time immediate payment │   │  upfront funding / lock       │
│  per-request billing        │   │  offchain vouchers            │
│                             │   │  periodic aggregated settle   │
└─────────────────────────────┘   └───────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Receipt Module                            │
│                                                                  │
│   standard payment receipt returned with protected resource      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Internal Design: How the Modules Work Together

The easiest way to understand MPP internally is to look at its two main execution paths: **charge** and **session**.

## Path 1: Charge Flow

This is the simpler model.

### Step-by-step flow

1. The client requests a resource.
2. The server determines that payment is required.
3. The server constructs a payment challenge and returns **402 Payment Required**.
4. The client SDK parses the challenge.
5. The client chooses a supported payment method.
6. The client fulfills the payment requirement and builds a payment credential.
7. The client retries the same request with **`Authorization: Payment`**.
8. The server verifies the credential and settles payment.
9. The server returns the resource with a **receipt**.

### Architectural meaning

The charge flow uses:
- the transport module
- the challenge module
- the credential module
- a method adapter
- the verification/settlement module
- the receipt module

This is the "pay once, get access" path.

---

## Path 2: Session Flow

This is the more advanced model.

### Step-by-step flow

1. The client requests access to a metered or streaming service.
2. The server responds with a session-oriented payment challenge.
3. The client opens the session by setting aside or locking funds.
4. The session becomes the authorization context for ongoing usage.
5. As the client consumes resources, it emits signed offchain vouchers or equivalent session proofs.
6. The server meters usage incrementally.
7. Settlement happens periodically or at session boundaries rather than per interaction.
8. The server continues serving requests or streaming output as long as the session remains valid and funded.

### Architectural meaning

The session flow adds:
- a session manager
- usage metering
- voucher handling
- deferred or aggregated settlement
- bounded continuous authorization

This is the module that makes MPP suitable for streaming and pay-as-you-go systems.

---

## Another Way to View the Internal Design

A concise internal decomposition is:

```text
MPP = HTTP Payment Auth Scheme
    + Challenge / Credential objects
    + Payment Method registry
    + Payment Intent registry
    + Verification / Settlement handlers
    + Receipt model
    + Session primitive
    + Discovery + SDK ecosystem
```

That decomposition is not just conceptual—it reflects how the published specifications separate:

- the base payment authentication scheme
- intent definitions
- method-specific specifications
- discovery metadata
- SDK implementations

---

## MPP's Design Philosophy

MPP's architecture follows a few important design principles.

## 1. Standardize the handshake, not just the rail

MPP does not try to reduce everything to one payment network.

Instead, it standardizes:

- how a payment is requested
- how a payment is authorized
- how the proof is returned
- how the result is conveyed

That means different rails can coexist under one interaction model.

---

## 2. Separate **method** from **intent**

This is one of the protocol's strongest design decisions.

- A **method** describes the payment rail and settlement details.
- An **intent** describes the semantic payment pattern.

Because of this separation, the protocol can support:
- one-time crypto payments
- one-time Stripe-backed payments
- session-based Tempo payments
- session-based Lightning flows
- future methods and future intents

without redesigning the whole transport layer.

---

## 3. Keep payment inside ordinary service calls

MPP is intentionally HTTP-native.

This matters because it preserves compatibility with:

- standard APIs
- fetch-based runtimes
- service middleware
- edge applications
- agent tool calls
- content delivery flows

It also means developers can add payments to existing services with less architectural disruption.

---

## 4. Optimize for real machine workloads, not just demos

The public materials emphasize that MPP is built for production concerns such as:

- idempotency
- expiration
- request binding
- continuous payments
- high-frequency, low-value workloads

That is why MPP includes sessions and safety primitives rather than stopping at a minimal 402 wrapper.

---

## 5. Treat discovery as an ecosystem feature, not a runtime requirement

The runtime 402 challenge is authoritative, but MPP's discovery model makes it easier for agents to understand payable services in advance.

This is especially relevant for:
- agent registries
- service catalogs
- monetized MCP servers
- API marketplaces
- payments directories

---

## How MPP Relates to Tempo

MPP is **not identical to Tempo**, but Tempo is a major implementation and settlement environment for MPP.

Public materials make this relationship clear:

- MPP is an **open standard**
- MPP runs on Tempo today
- the protocol is designed to be **rail-agnostic**
- Tempo supplies a strong settlement layer for stablecoin-based machine payments
- Tempo's own architecture makes sessions and payment-heavy workloads especially practical

So the right mental model is:

> **Tempo is one important settlement environment and implementation path for MPP.**
>
> **MPP itself is the broader payment protocol.**

---

## How MPP Relates to x402

MPP can be understood independently, but it is helpful to note one compatibility point:

- MPP is **backwards-compatible with x402**
- x402's core exact-payment flow maps directly to MPP's **`charge`** intent

That means MPP can be viewed as the larger framework, with x402-style request billing fitting inside it as a subset.

In practice, this is important because it allows existing pay-per-request systems to evolve toward richer session and multi-rail models without abandoning the familiar 402 pattern.

---

## The Most Important Design Insight

If you only remember one architectural point, remember this:

> **MPP separates the payment handshake from the payment rail.**

That is what allows it to combine:

- ordinary HTTP ergonomics
- multiple payment methods
- multiple payment intents
- receipts
- discovery
- and session-based continuous payments

inside one coherent protocol family.

---

## Practical Summary

If someone asks, **"What are the main modules of MPP?"**, the cleanest answer is:

1. **Transport / authentication**
2. **Challenge**
3. **Credential**
4. **Payment methods**
5. **Payment intents**
6. **Verification / settlement**
7. **Receipt**
8. **Sessions**
9. **Discovery**
10. **SDK / middleware runtime**

If someone asks, **"What is MPP's internal design?"**, the best concise answer is:

> **MPP is an HTTP-native payment protocol that standardizes the challenge–credential–receipt loop, separates methods from intents, and adds session-based continuous payment primitives on top of a rail-agnostic settlement model.**

---

## Bottom Line

MPP is best understood as a **machine-payment protocol stack**, not just a payment API.

Its internal architecture is modular:

- HTTP-native transport and authentication
- standardized challenges and credentials
- pluggable payment methods
- reusable payment intents
- method-specific settlement
- standard receipts
- session-based streaming payments
- optional service discovery
- SDKs and middleware for production use

That modular design is exactly what makes MPP suitable for the next generation of agentic commerce, monetized APIs, streaming services, and machine-to-machine internet payments.

---

## References

- MPP overview: https://docs.stripe.com/payments/machine/mpp
- Stripe blog: Introducing the Machine Payments Protocol: https://stripe.com/blog/machine-payments-protocol
- Tempo mainnet / MPP announcement: https://tempo.xyz/blog/mainnet
- Privy: Building on Tempo's Machine Payments Protocol: https://privy.io/blog/building-on-privy-with-tempo-machine-payments-protocol
- Cloudflare Agents docs — MPP overview: https://developers.cloudflare.com/agents/agentic-payments/mpp/
- Payment HTTP Authentication Scheme: https://paymentauth.org/
- Payment discovery specification: https://paymentauth.org/draft-payment-discovery-00.html
- Charge intent specification: https://paymentauth.org/draft-payment-intent-charge-00.html
- Tempo charge method specification: https://paymentauth.org/draft-tempo-charge-00.html
- Tempo session intent specification: https://paymentauth.org/draft-tempo-session-00.html
