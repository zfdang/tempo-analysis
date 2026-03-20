# Tempo Overview

## What Tempo Is

Tempo is not a single wallet product. It is a broader payments stack centered on a payment-optimized Layer 1 blockchain, machine payments, stablecoin infrastructure, and developer tooling. Tempo is a blockchain purpose-built for payments, with a focus on stablecoins, low-cost transfers, high throughput, and machine-native commerce.

Tempo was incubated by **Paradigm** and **Stripe**. Tempo Mainnet launched on **March 18, 2026**, alongside the **Machine Payments Protocol (MPP)**, an open standard for machine payments co-authored with Stripe.

The Tempo stack combines several layers:

- a payment-focused L1 network
- protocol-level transaction primitives for payments
- a stablecoin standard
- a machine payments protocol
- wallet, CLI, and SDK tooling
- supporting infrastructure such as explorer, contract verification, token lists, and fee sponsorship services

## Core Product Areas

### 1. Tempo Mainnet / Payment Network

At the center of the stack is the Tempo network itself: a Layer 1 blockchain optimized for payment use cases. The public positioning emphasizes:

- stablecoin-native payments
- low fees
- high throughput
- global transfers
- payment-focused blockspace
- EVM compatibility

The product story is less about generalized speculation and more about real payment flows such as remittances, payroll, payouts, embedded finance, and agentic commerce.

### 2. Tempo Transactions

One of Tempo's most important protocol-level features is its custom transaction model, the `0x76` Tempo Transaction type. These are payment-native transactions that support:

- passkey / WebAuthn authentication
- batch calls
- scheduled payments
- concurrent or parallel transaction flows
- fee sponsorship

This is a major part of Tempo's value proposition: turning common payment workflow requirements into protocol-level primitives instead of leaving everything to app-layer smart contract design.

### 3. TIP-20 Stablecoin Standard

Tempo introduces TIP-20, its stablecoin-oriented token standard. TIP-20 extends familiar ERC-20 token behavior with additional payment-related features such as:

- transfer memos
- compliance or policy hooks
- reward distribution support
- use as a fee token on the network

This makes TIP-20 part of Tempo's stablecoin infrastructure story rather than just a generic token format.

### 4. Machine Payments Protocol (MPP)

Another major product line is MPP, the Machine Payments Protocol. MPP is an open standard for machine payments, co-authored with Stripe, that targets AI agents and machine-to-machine commerce.

MPP is built around HTTP payment flows. The core idea is that an application, agent, or user can request a service, receive payment requirements (via HTTP 402), and complete payment within the request flow instead of relying on API keys, monthly billing, or traditional checkout systems.

MPP is designed to be rail-agnostic and extensible. At launch, it supports multiple payment methods including Tempo stablecoins, Stripe-backed fiat, Visa card payments, and Lightning network Bitcoin payments.

This makes MPP central to Tempo's "agent economy" narrative.

## User-Facing and Developer-Facing Products

### 1. Tempo Wallet

Tempo Wallet is more than a normal blockchain wallet. It includes both:

- a web wallet / login flow
- a CLI wallet and HTTP client

Its positioning focuses heavily on enabling AI agents or applications to pay for services on demand. Key wallet-related ideas include:

- passkey login
- session keys
- scoped delegated spending
- machine payment requests
- streaming or session-based payments

This makes the wallet closer to an agent payment tool than a conventional retail wallet.

### 2. CLI

Tempo's CLI is a practical interface for developers and agents. It supports:

- wallet creation
- funding and key management
- direct requests to paid services
- native handling of payment-required responses
- session authorization for local or delegated usage

### 3. SDKs

Tempo provides a growing tooling ecosystem for developers. Public repositories include support for multiple languages:

- TypeScript
- Go
- Python
- Rust

These SDKs appear to cover both network interaction and machine payment flows.

### 4. Foundry and Standard Library

Tempo has built custom developer tooling around smart contract development, including:

- a Tempo-specific Foundry distribution
- a Tempo standard library with payment-oriented interfaces and contracts

This suggests a deliberate effort to make payment-native contract development easier for builders.

## Supporting Infrastructure

Tempo's public repositories and docs also point to an infrastructure layer that includes:

- block explorer
- contract verification service
- token list registry
- key management tooling
- fee payer / sponsor service

These components are important because they make Tempo look like a full platform rather than just a protocol spec.

## Product Direction

Based on its official documentation and mainnet launch materials, Tempo is pursuing several product theses.

### A. Stablecoin Payments as Core Infrastructure

Tempo clearly treats stablecoins as a first-class payment primitive. That shows up in:

- stablecoin fee support
- stablecoin transaction standards
- payment-focused transaction design
- exchange / swap infrastructure

### B. Machine Payments and Agent Commerce

Tempo is also clearly aiming at AI-native commerce. The combination of MPP, session keys, passkeys, wallet tooling, and HTTP payment flows suggests a future where:

- agents discover services
- services return payment requirements
- payments are made in-request
- results are unlocked programmatically

This is one of the strongest differentiators in Tempo's public positioning.

### C. Protocol-Level Payment UX

A recurring theme is moving payment UX improvements into protocol design. Instead of requiring every application to rebuild the same abstractions, Tempo appears to provide them as core primitives:

- sponsored fees
- delegated sessions
- programmable payment flows
- scheduling
- batching

### D. Developer-First Payment Stack

Tempo does not appear to be only a consumer wallet brand. It is also a developer platform with protocol specs, SDKs, wallet tooling, infra services, and contract development tools.

## How to Think About the Stack

A useful way to understand Tempo is as a five-layer system:

1. **Application Layer**  
   Agent apps, paid APIs, service marketplaces, routing, search, and business logic.

2. **Wallet / Identity Layer**  
   Passkeys, WebAuthn, session keys, wallet UX, CLI authorization.

3. **Machine Payments Layer**  
   MPP, HTTP payment flows, session payments, streaming payments.

4. **Protocol Layer**  
   Tempo Transactions, TIP-20, fee sponsorship, payment-aware smart account behavior, stablecoin-related protocol features.

5. **Network Layer**  
   Tempo mainnet itself: the L1 execution and settlement layer.

This framing helps separate what is definitely part of Tempo's public core from what may be app-specific integrations built on top of it.

## What Is Probably Tempo Core vs. App-Specific

One important distinction is that not everything associated with Tempo is necessarily part of Tempo's canonical protocol architecture.

The following are core product areas:

- Tempo mainnet
- Tempo Transactions (`0x76`)
- TIP-20 and TIP-403
- TIP-20 Rewards
- Fee Manager and Fee AMM
- Stablecoin DEX
- pathUSD
- MPP
- wallet / CLI / SDKs
- explorer / verification / token list / fee payer services

By contrast, some ideas often discussed around Tempo are better treated as optional or application-specific, for example:

- service search
- intent matching
- virtual cards
- escrow services
- TEE-based execution environments
- custom facilitator layers

Those may be useful integrations or product designs built on Tempo, but they should not automatically be treated as first-party protocol components unless explicitly documented as such.

## Why Tempo Matters

Tempo is interesting because it tries to connect three worlds that are often separate:

- blockchain settlement
- stablecoin payments
- machine-native commerce

Many crypto systems support tokens but do not optimize for payment UX. Many payment systems support good UX but do not expose machine-native programmable settlement. Many AI products need pay-per-call commerce but still rely on API keys and account billing.

Tempo's public strategy seems to be to bridge those gaps with:

- payment-oriented chain design
- payment-native transaction types
- machine payment protocols
- stablecoin standards
- developer tooling for real integration

## Bottom Line

Tempo should be understood as a payment platform stack, not just a wallet or just a blockchain.

Its public product footprint includes:

- a payment-focused Layer 1 network
- payment-native transaction primitives
- a stablecoin token standard
- a machine payments protocol
- wallet and CLI tooling
- developer SDKs
- core infrastructure services

The most distinctive part of the story is the combination of stablecoin payments and AI-agent payment flows. That is where Tempo looks meaningfully different from a typical crypto network or a conventional wallet product.
