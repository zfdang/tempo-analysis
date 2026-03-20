# Tempo Application Layer: Functions and Modular Design

## Overview

Tempo's **application layer** is best understood not as a single contract or SDK, but as the **developer-facing capability layer** built on top of Tempo's payment-oriented protocol primitives.

At the top level, Tempo presents four clear application surfaces:

1. **Payments**
2. **Stablecoin issuance and operations**
3. **Stablecoin exchange and routing**
4. **Machine payments / agent commerce**

Underneath those surfaces, Tempo exposes a set of tightly related protocol modules that make those applications possible, including:

- **TIP-20**
- **TIP-403**
- **TIP-20 Rewards**
- **Tempo Transactions**
- **Fees + Fee AMM**
- **Blockspace / payment lanes**
- **Stablecoin DEX**
- **MPP (Machine Payments Protocol)**

A concise summary is:

> **Tempo's application layer is a payment-first application stack built from protocol-native modules rather than from loosely connected dApps.**

---

## What the Tempo Application Layer Does

Tempo's application layer is designed around real payment workflows rather than generic smart-contract deployment alone.

From the official docs and launch materials, the main functions are:

### 1. Stablecoin payments

Tempo's payment guides highlight a set of application-facing payment features:

- sending payments
- accepting payments
- attaching memos for reconciliation
- paying fees in supported stablecoins
- sponsoring user fees
- sending parallel transactions

This means Tempo treats practical payment concerns—such as reconciliation, fee abstraction, and throughput—as first-class application capabilities rather than afterthoughts.

---

### 2. Stablecoin issuance and token operations

Tempo's TIP-20 standard is designed specifically for **stablecoins and payment tokens**. It supports not only fungible-token basics, but also payment-oriented operational features such as:

- transfer memos
- role-based administrative controls
- supply caps
- pause / unpause controls
- transfer policy integration
- currency declaration
- quote-token configuration
- rewards distribution

This turns issuance into more than "deploy a token contract." It gives builders a more complete token-operations layer for payment products.

---

### 3. Stablecoin exchange and routing

Tempo includes an **enshrined decentralized exchange** focused on stablecoin-to-stablecoin trading, especially between tokens representing the same underlying fiat denomination or asset family.

For applications, this enables:

- cross-stablecoin swaps
- routing between payment assets
- liquidity-aware settlement paths
- quote-token-based exchange structure

That makes exchange a native part of the application stack rather than something developers must always source from an external protocol.

---

### 4. Machine payments and agent commerce

Tempo also positions **MPP (Machine Payments Protocol)** as part of the application-facing layer for agentic commerce.

The public docs and launch materials describe this surface as enabling:

- machine-to-machine payments
- sessions and streaming payments
- paid API calls
- monetized MCP servers
- gated services and content
- multi-service agent workflows

This expands Tempo's application layer beyond user wallets and merchant payments into **agent-driven internet commerce**.

---

## The Best Way to Think About the Architecture

A useful mental model is:

```text
Tempo Application Layer
├── Payments Apps
├── Stablecoin Issuance & Operations
├── Stablecoin Exchange & Routing
└── Machine Commerce / MPP

Built on:

├── TIP-20 assets
├── TIP-403 policies
├── TIP-20 Rewards
├── Tempo Transactions
├── Fees + Fee AMM
├── Blockspace / payment lanes
└── Stablecoin DEX
```

This architecture is distinctive because many functions that are often left to application logic on other chains are instead provided by Tempo as **protocol-native modules**.

---

## Top-Level Application Modules

## 1. Payments Apps

This module includes the capabilities developers need to build payment flows directly into products.

Typical functions include:

- peer-to-peer transfers
- merchant acceptance flows
- payouts and disbursements
- reconciliation through transfer memos
- stablecoin-denominated fee payment
- gas sponsorship
- parallel submission for high-volume operations

This module is the most direct expression of Tempo's "payments-first" philosophy.

---

## 2. Stablecoin Issuance & Operations

This module serves builders issuing or operating stablecoins and payment tokens.

It includes:

- token creation
- mint / burn workflows
- supply caps
- pause controls
- permissioned administrative roles
- compliance policy attachment
- rewards distribution
- operational configuration for routing and fees

This makes Tempo useful not only for using stablecoins, but also for **operating them as payment products**.

---

## 3. Stablecoin Exchange & Routing

This module provides the exchange and liquidity layer for payment assets.

It includes:

- stablecoin swaps
- quote-token routing
- orderbook-based liquidity
- exchange support for like-kind stablecoins
- token conversion paths needed for payments and fees

Because exchange is built into the protocol, Tempo can support payment routing and stablecoin interoperability more directly than systems that depend entirely on external DEX infrastructure.

---

## 4. Machine Commerce / MPP

This module supports agentic and programmatic commerce.

It includes:

- machine-to-machine payment requests
- 402-style paid resource access
- request / authorize / settle flows
- sessions for continuous payments
- streaming and pay-per-use interactions
- multi-service payment-aware workflows

In practical terms, this is the part of Tempo's application layer that lets APIs and services become directly monetizable for software agents.

---

## Core Supporting Protocol Modules

The application layer above is powered by a set of lower-level modules. These modules are where Tempo's design becomes especially opinionated.

## 1. TIP-20: the asset module

TIP-20 is Tempo's native token standard for stablecoins and payment tokens.

It is the foundation for:

- payment assets
- fee payment eligibility
- payment lanes
- DEX quote-token behavior
- routing metadata
- transfer memos
- reward distribution
- issuer controls

In architectural terms, TIP-20 is the **money object layer** of the Tempo application stack.

---

## 2. TIP-403: the policy and compliance module

TIP-403 is Tempo's policy registry.

Instead of requiring each token to implement its own compliance logic, TIP-403 allows policies to be defined once and shared across multiple TIP-20 tokens.

This gives Tempo a reusable policy layer for:

- access control
- whitelist / blacklist logic
- compliance enforcement
- governance-oriented token controls

Architecturally, TIP-403 acts as the **shared policy control plane** for tokenized payment systems.

---

## 3. TIP-20 Rewards: the incentive module

TIP-20 Rewards is a built-in rewards distribution mechanism for opted-in holders.

Its purpose is to make rewards distribution:

- integrated directly into token behavior
- efficient at scale
- simpler for wallets
- compliant with TIP-403 transfer policies

This turns rewards into a protocol-native feature rather than requiring a separate staking or rewards contract for common cases.

Architecturally, this is Tempo's **issuer incentive and distribution module**.

---

## 4. Tempo Transactions: the execution module

Tempo Transactions are a protocol-native transaction type designed specifically for Tempo.

They provide:

- configurable fee tokens
- fee sponsorship
- batch calls
- access keys
- concurrent transactions
- scheduled transactions
- passkey / P256 / WebAuthn compatibility

This is one of the most important modules in the entire system.

Why? Because it acts as the **execution API** for the application layer. Whether a developer is building payments, disbursements, subscriptions, agent workflows, or token operations, these features define how those workflows actually execute.

Architecturally, Tempo Transactions are the **application execution engine**.

---

## 5. Fees + Fee AMM: the fee settlement module

Tempo has no native token for fees in the traditional sense. Instead, supported stablecoins can be used to pay both gas fees and priority fees.

The Fee AMM handles conversion between:

- the user's chosen fee token
- the validator's preferred fee token

This is important because it allows Tempo applications to present a more intuitive payment UX:

- users do not need to acquire a separate gas asset
- applications can be built around stablecoin-native fee logic
- payment flows remain coherent with the rest of the asset model

Architecturally, this module is Tempo's **fee abstraction and fee-conversion layer**.

---

## 6. Blockspace / payment lanes: the throughput and QoS module

Tempo extends the Ethereum block format to include:

- payment lanes
- shared gas limits
- sub-block support
- system transactions for protocol operations

This matters at the application layer because it means payment traffic can receive dedicated treatment.

The result is a system better suited for:

- large payout runs
- predictable payment fees
- payment-heavy workloads
- reduced interference from unrelated onchain activity

Architecturally, this is the **execution-quality and throughput-guarantee layer** of Tempo's application stack.

---

## 7. Stablecoin DEX: the liquidity module

Tempo's Stablecoin DEX is an enshrined exchange designed specifically for stablecoin trading.

It includes:

- an orderbook structure
- price-time priority
- quote-token based market structure
- limit orders
- flip orders
- market orders via swaps

For applications, this means the protocol itself can help solve liquidity and routing problems that often become painful in payment systems.

Architecturally, this is the **liquidity and routing module**.

---

## 8. MPP: the machine-payments interface module

MPP sits at the edge between Tempo and application services.

It provides a protocol for:

- requesting payment
- authorizing payment
- settling payment
- running session-based payment flows
- streaming usage-based payments

MPP matters because it extends Tempo's application model from "wallet-to-wallet" and "app-to-chain" patterns into **service-to-agent commerce**.

Architecturally, this is the **programmatic commerce interface layer**.

---

## A Layered Module Diagram

Below is a practical view of how these modules relate to one another:

```text
┌────────────────────────────────────────────────────────────┐
│                 Tempo Application Layer                    │
│                                                            │
│  1. Payments Apps                                          │
│  2. Stablecoin Issuance & Operations                       │
│  3. Stablecoin Exchange & Routing                          │
│  4. Machine Commerce / MPP                                 │
└────────────────────────────────────────────────────────────┘
                           │
      ┌────────────────────┼────────────────────┬────────────────────┐
      │                    │                    │                    │
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   TIP-20     │   │   TIP-403    │   │ TIP-20       │   │ Stablecoin   │
│   Assets     │   │   Policies   │   │ Rewards      │   │ DEX          │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
      │                    │                    │                    │
      └────────────────────┴──────────────┬─────┴────────────────────┘
                                          │
                              ┌──────────────────────────┐
                              │   Tempo Transactions     │
                              │   batching / sponsorship │
                              │   passkeys / access keys │
                              │   scheduling / parallel  │
                              └──────────────────────────┘
                                          │
                              ┌──────────────────────────┐
                              │     Fees + Fee AMM       │
                              │ stablecoin fee payment   │
                              │ fee-token conversion     │
                              └──────────────────────────┘
                                          │
                              ┌──────────────────────────┐
                              │ Blockspace / QoS Layer   │
                              │ payment lanes / subblocks│
                              └──────────────────────────┘
```

This diagram is intentionally simplified, but it reflects the basic design philosophy well:

> **Tempo moves payment-critical functions into protocol-native modules so developers can compose payment applications more directly.**

---

## Why This Design Matters

Tempo's application layer is notable for three reasons.

### 1. It is not "generic chain first"

Tempo does not simply expose a smart-contract environment and leave payment developers to assemble the rest themselves. Instead, it bakes payment primitives directly into protocol features.

That changes the development experience.

On many chains, a builder must combine:

- a fungible-token standard
- custom compliance logic
- some DEX or router
- some gas-abstraction mechanism
- some smart-wallet pattern
- separate rewards logic
- custom reconciliation conventions

Tempo tries to make many of those features protocol-native.

---

### 2. The modules are strongly related, but clearly scoped

Tempo's design is not monolithic in the sense of one giant payment contract.

Instead, each module has a clear role:

- **TIP-20** defines payment assets
- **TIP-403** defines shared policy logic
- **TIP-20 Rewards** defines token reward distribution
- **Tempo Transactions** defines how applications execute actions
- **Fees + Fee AMM** defines how fees are paid and converted
- **Blockspace** defines throughput and reserved capacity
- **Stablecoin DEX** defines liquidity and routing
- **MPP** defines agent-facing machine payment flows

This creates a system that is opinionated, but still modular.

---

### 3. The real target is end-to-end payment workflows

Tempo's design makes the most sense when viewed through real payment workloads such as:

- payroll
- payouts
- remittances
- embedded finance
- tokenized deposits
- pay-per-call APIs
- monetized data services
- agentic commerce

The application layer is therefore not just an app SDK layer. It is a **workflow-oriented architecture for moving value predictably and programmatically**.

---

## Practical Summary

If someone asks, "What is Tempo's application layer?" the best answer is:

> **It is a payments-first developer platform made of protocol-native modules for assets, compliance, execution, fees, liquidity, throughput, incentives, and machine payments.**

If someone asks, "What are its main functions?" the cleanest summary is:

- **payments**
- **stablecoin issuance**
- **stablecoin exchange**
- **machine payments**

If someone asks, "How is it designed?" the cleanest answer is:

- **top-level application modules**
- built on
- **protocol-native support modules**
- all optimized for payment workflows rather than generic onchain activity

---

## Bottom Line

Tempo's application layer is not a thin UI layer on top of a generic blockchain.

It is a **modular payment application stack** built from protocol-native primitives:

- TIP-20 for assets
- TIP-403 for policy
- TIP-20 Rewards for incentives
- Tempo Transactions for execution
- Fees + Fee AMM for fee abstraction
- Blockspace for predictable throughput
- Stablecoin DEX for routing and liquidity
- MPP for machine commerce

That is what makes Tempo's application layer distinctive: it is designed to help builders compose complete payment systems, not just deploy isolated contracts.

---

## References

- Tempo Docs — Home: https://docs.tempo.xyz/
- Tempo Docs — Stablecoin Payments: https://docs.tempo.xyz/guide/payments
- Tempo Docs — Tempo Protocol Overview: https://docs.tempo.xyz/protocol
- Tempo Docs — TIP-20 Overview: https://docs.tempo.xyz/protocol/tip20/overview
- Tempo Docs — TIP-403 Overview: https://docs.tempo.xyz/protocol/tip403/overview
- Tempo Docs — Fees Overview: https://docs.tempo.xyz/protocol/fees
- Tempo Docs — Tempo Transactions: https://docs.tempo.xyz/protocol/transactions
- Tempo Docs — Blockspace Overview: https://docs.tempo.xyz/protocol/blockspace/overview
- Tempo Docs — Stablecoin DEX Overview: https://docs.tempo.xyz/protocol/exchange
- Tempo Docs — TIP-20 Rewards Overview: https://docs.tempo.xyz/protocol/tip20-rewards/overview
- Tempo Blog — Mainnet Launch / MPP overview: https://tempo.xyz/blog/mainnet
