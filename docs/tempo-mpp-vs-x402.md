# Tempo MPP vs. x402

## Overview

Tempo's **Machine Payments Protocol (MPP)** and the standard **x402** flow share the same core idea: a client requests a paid resource, the server responds with an HTTP **402 Payment Required** challenge, the client presents payment authorization, and the server returns the resource if payment is valid.

But they are not the same thing.

A useful way to think about them is:

- **x402** is a lightweight HTTP-native payment standard for paid API requests.
- **Tempo MPP** is a broader machine-commerce protocol layer that is compatible with x402-style flows, while adding session support, multi-rail payment support, richer request binding, receipts, and production-oriented controls.

In other words:

> **x402 is a pay-per-request protocol pattern.**
>  
> **MPP is a broader protocol framework for machine payments.**

---

## High-Level Comparison

### What they have in common

Both x402 and Tempo MPP:

1. Use **HTTP 402 Payment Required** as the starting challenge model.
2. Allow a client or agent to request a resource first, then pay only when challenged.
3. Support a **challenge -> authorization -> retry** interaction pattern.
4. Return the requested resource only after payment is validated.
5. Are designed to make machine-to-machine payments feel native to API calls rather than requiring pre-funded accounts or manual checkout flows.

### Where they differ

The biggest differences are in **scope** and **execution model**.

#### x402

x402 is primarily focused on **per-request monetization**. A single API request is challenged, the client signs or otherwise prepares the payment payload, retries the request, and the server verifies it.

This model is clear, simple, and well-suited for discrete paid requests.

#### Tempo MPP

MPP includes the x402-style charge flow, but extends it with more machine-commerce primitives, especially:

- **Sessions**
- **Streaming / usage-based interaction**
- **Multi-rail payment support**
- **Receipts as protocol objects**
- **Request binding**
- **Expiration and idempotency controls**
- **Periodic settlement models**

So while x402 is centered on **one paid request at a time**, MPP is designed for **ongoing agent interactions**, including high-frequency and low-value workloads.

---

## Layered Architecture Comparison

Below is a practical layered view of **Tempo MPP vs. x402**.

```text
┌─────────────────────────────────────────────────────────────┐
│  L7 Application / Agent Workflow Layer                     │
│  x402:  Paid API call / tool call / MCP call               │
│  MPP :  API call + multi-step commerce + streaming usage   │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L6 Business Intent / Payment Intent Layer                 │
│  x402:  Primarily per-request charging                     │
│  MPP :  charge + session + extensible payment intents      │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L5 Session / Execution Model Layer                        │
│  x402:  request -> authorize -> retry                      │
│  MPP :  per-request + session + vouchers + periodic        │
│         settlement                                         │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L4 Protocol Control Layer                                 │
│  x402:  402 + payment challenge + signed retry             │
│  MPP :  challenge + credential + receipt + request        │
│         binding + expiration + idempotency                │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L3 Payment Method Abstraction Layer                       │
│  x402:  Mostly blockchain-centered payment flows           │
│  MPP :  Multi-rail: stablecoins / cards / Lightning /      │
│         custom rails / Stripe rails                        │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L2 Settlement Layer                                       │
│  x402:  Facilitator + on-chain authorization/verification  │
│  MPP :  Method-specific settlement                         │
│         (on-chain or processor-native settlement)          │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│  L1 Wallet / Signature / Identity Layer                    │
│  x402:  Local wallet signs payment payload                 │
│  MPP :  Agent wallet + delegated execution + funding       │
│         flows + identity integration                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Explanation

### L7. Application / Agent Workflow Layer

At the top level, **x402** is usually used to monetize a single API request or tool invocation. It fits naturally into paid HTTP endpoints, MCP tools, and machine-readable service calls.

**MPP** operates at the same application boundary, but is designed for broader machine-commerce workflows. Instead of just "this request costs money," MPP can support longer-running interactions, continuous usage, and multi-step payment-aware workflows.

**Practical interpretation:**

- x402: "Pay for this request."
- MPP: "Pay for this request, or for this ongoing machine interaction."

---

### L6. Business Intent / Payment Intent Layer

At this layer, x402 is conceptually narrow and elegant: the server charges for a request.

MPP generalizes that model by introducing a richer set of payment intents. Public descriptions of MPP make it clear that x402-style flows map well to MPP's **charge** model, but MPP also introduces **session-oriented** flows and broader payment semantics.

**Practical interpretation:**

- x402: one charging model
- MPP: multiple charging and authorization models

---

### L5. Session / Execution Model Layer

This is the most important architectural distinction.

In x402, the dominant model is:

1. Client sends request
2. Server returns 402 challenge
3. Client prepares payment authorization
4. Client retries request
5. Server verifies and returns resource

MPP still supports that model, but it also adds **session-based execution**. A session can support repeated interactions, off-chain vouchers, and eventual or periodic settlement.

This makes MPP better suited for:

- streaming usage
- many tiny calls
- long-running agent tasks
- continuous service consumption

**Practical interpretation:**

- x402: per-request execution
- MPP: per-request or session-based execution

---

### L4. Protocol Control Layer

This layer includes the protocol objects and anti-abuse controls.

x402 standardizes the challenge-response shape around HTTP 402 and signed retries. It is deliberately lightweight.

MPP adds stronger protocol control semantics, including:

- payment challenge objects
- payment credentials
- receipts
- request binding
- expiration controls
- idempotency support

These additions matter in production because they help prevent:

- replay attacks
- duplicate charges
- misbinding payments to the wrong request
- retry confusion in distributed systems

**Practical interpretation:**

- x402: minimal payment control plane
- MPP: production-grade machine payment control plane

---

### L3. Payment Method Abstraction Layer

x402 is usually discussed in the context of blockchain-native payments, especially stablecoins and on-chain authorization flows.

MPP is more expansive. It is described as supporting **multi-rail payments**, including not only crypto-based payment methods but also card-style and processor-backed payment rails, depending on the deployment environment.

This changes the role of the protocol:

- x402 feels like a blockchain-native paid API standard.
- MPP feels like a unified machine payment abstraction.

**Practical interpretation:**

- x402: chain-first payment abstraction
- MPP: rail-agnostic payment abstraction

---

### L2. Settlement Layer

In x402, settlement is often tied to a facilitator and blockchain verification flow.

MPP allows settlement to vary by payment method. If a method is crypto-native, settlement can be on-chain. If a method uses processor-backed rails, settlement can follow that processor's flow.

This makes MPP more flexible for real-world deployment, especially where machine payments need to bridge crypto and traditional payment infrastructure.

**Practical interpretation:**

- x402: more uniform settlement path
- MPP: method-specific settlement path

---

### L1. Wallet / Signature / Identity Layer

Both systems need a cryptographic or authorization-capable identity on the client side.

In x402, that usually means a programmatic wallet signing the payment payload locally.

MPP can use similar signing infrastructure, but it is more naturally aligned with a richer agent runtime stack:

- agent wallet provisioning
- delegated execution
- funding management
- identity integration
- automated payment authorization

So while both require a payment-capable machine identity, MPP more naturally plugs into a complete agent infrastructure stack.

**Practical interpretation:**

- x402: wallet-enabled payer
- MPP: identity-aware agent payment runtime

---

## The Core Relationship

The most accurate summary is this:

> **Tempo MPP does not reject the x402 model.**
>  
> **It absorbs and extends it.**

A typical x402 charge flow can be viewed as a **subset** or **special case** of a broader MPP architecture.

That means:

- If you only need simple paid API requests, x402 may be enough.
- If you need sessions, streaming, multi-rail support, or more production-oriented controls, MPP is the richer framework.

---

## Engineering Takeaway

From a systems design perspective:

```text
x402 = a clean HTTP-native pay-per-request payment standard

MPP  = x402-style challenge/retry
       + session support
       + multi-rail support
       + richer protocol controls
       + broader machine-commerce semantics
```

So if you are designing agent infrastructure:

- Choose **x402** when you want a simple, explicit, request-level payment pattern.
- Choose **MPP** when you want a broader payment runtime for machine agents, especially when continuous usage, sessionization, or payment-rail flexibility matters.

---

## Conclusion

Tempo's MPP and x402 are closely related, but they operate at different levels of ambition.

**x402** gives you a clean and understandable standard for paid HTTP requests.

**MPP** builds on that idea and turns it into a broader machine-payment protocol layer suitable for agent systems, richer workflow orchestration, and multi-rail settlement environments.

That is why the clearest mental model is:

- **x402 = paid request standard**
- **MPP = machine payments framework that includes paid requests and more**
