# Tempo Protocol Components Guide

This document expands the earlier Tempo component diagram into a written guide. It explains what each component is, what job it performs, how it connects to adjacent layers, and how developers or users typically encounter it.

The organization here is intentionally bottom-up. We start with the lowest layers of settlement and execution, then move upward through transactions, assets, identity, machine payments, and finally applications.

---

## 1. How to Read the Tempo Stack

A useful way to understand Tempo is as a layered payment stack, read from the top downward:

1. **Application Layer**  
   Agents, apps, paid services, routing, and business logic.

2. **Machine Payments Layer**  
   HTTP 402 flows, MPP, session payments, and streaming payments.

3. **Wallet and Identity Layer**  
   Wallet UX, passkeys, session keys, and key management.

4. **Asset and Stablecoin Layer**  
   TIP-20, stablecoin fee behavior, policy hooks, and exchange primitives.

5. **Transaction Layer**  
   Tempo Transactions as the protocol-native transaction model.

6. **Network and Execution Layer**  
   Tempo mainnet, execution, finality, and payment-aware blockspace.

This ordering matters because it separates components that are easy to blur together.

The stack overview above is intentionally top-down because it starts from what users and developers usually see first. The detailed sections below switch to a bottom-up explanation so the architecture can be built from settlement and execution upward.

In particular:

- **Tempo Transactions** belong to the **transaction layer**
- **TIP-20** belongs to the **asset layer**

They interact closely, but they are not the same thing. A transaction type defines how actions are represented, signed, validated, and executed. A token standard defines how assets behave on the network.

---

## 2. Network and Execution Layer

This is the base of the stack. Everything above it depends on Tempo's ability to execute transactions, settle state changes, and provide predictable inclusion and finality.

### 2.1 Tempo Mainnet / L1

This is the settlement and execution environment itself.

**What this component does**
- Executes transactions
- Settles payment flows
- Hosts native asset and stablecoin activity
- Provides the foundation for the rest of the stack

**How developers encounter it**
- Through RPC endpoints
- Through wallets and SDKs
- Through contract deployment and transaction submission

### 2.2 EVM-Compatible Execution

Tempo presents itself as EVM-compatible.

**What this component does**
- Makes the network more accessible to Ethereum-aligned developers
- Supports familiar smart contract workflows and tooling
- Lowers migration and integration cost for builders

**Why it matters**
Tempo can introduce payment-specific features without forcing developers to abandon the broader EVM ecosystem.

### 2.3 Consensus and Performance Layer

Tempo's public materials emphasize low-latency settlement and payment-oriented performance.

**What this component does**
- Supports low-latency transaction confirmation
- Improves responsiveness for payment use cases
- Helps the chain meet machine-payment and user-payment requirements

**Why it matters**
Payments and agent interactions are much more sensitive to latency and confirmation behavior than many speculative blockchain use cases.

### 2.4 Payment-Focused Blockspace / Payment Lanes

Tempo documentation references payment lanes or protected payment blockspace.

**What this component does**
- Reserves capacity for payment transactions
- Helps protect payment flows from unrelated congestion
- Improves reliability for payment-driven transaction inclusion

**Why it matters**
This is one of the clearest examples of Tempo optimizing the network for payments, not merely allowing payments as one possible use case.

---

## 3. Transaction Layer

This layer sits directly above network execution. It defines how users and applications express actions to the chain.

### 3.1 Tempo Transactions

Tempo Transactions are one of the signature protocol features of the network.

**What this component does**
- Provides a payment-native transaction type
- Supports passkey-compatible authentication flows
- Supports batching
- Supports scheduling
- Supports parallel or concurrent transaction patterns
- Supports fee sponsorship

**Why it matters**
Tempo Transactions move important payment and account UX concerns into the protocol itself. Instead of forcing every application to rebuild the same abstractions using wrapper contracts or external infrastructure, Tempo treats them as native transaction behavior.

**Who uses it**
- Wallet developers
- App developers using Tempo SDKs
- Infrastructure builders
- Anyone building higher-level payment flows on Tempo

### 3.2 Fees and Fee Sponsorship

Tempo treats fee behavior as an important part of the transaction model.

**What this component does**
- Supports sponsored transaction flows
- Allows third parties to pay fees for end users
- Reduces friction in onboarding and service usage
- Connects transaction submission to Tempo's broader payment design

**Why it matters**
Sponsored fees are critical when you want users or agents to access a service without managing every low-level network step themselves.

### 3.3 Why This Is a Separate Layer from TIP-20

It is useful to be explicit here:

- Tempo Transactions define how actions are packaged and validated
- TIP-20 defines how stablecoin-like assets behave once those actions execute

The transaction layer is about:

- transaction format
- signatures
- nonce behavior
- batching
- sponsorship
- execution semantics

The asset layer is about:

- balances
- transfers
- memos
- policies
- fee-token eligibility

Keeping these separate makes the stack easier to reason about.

---

## 4. Asset and Stablecoin Layer

This layer defines the payment assets that flow through Tempo. It is adjacent to the transaction layer, but conceptually distinct from it.

### 4.1 TIP-20 Stablecoin Standard

TIP-20 is Tempo's stablecoin-oriented token standard.

**What this component does**
- Defines native stablecoin behavior on the network
- Supports payment- and reconciliation-friendly flows
- Enables payment metadata such as memos
- Connects assets to policy and rewards systems

**Why it matters**
Tempo is designed around stablecoin payments, so the token standard is not a side detail. It is a major part of the overall payment model.

### 4.2 Stablecoin Fees

Tempo's public documentation emphasizes that stablecoins can play a direct role in fee handling.

**What this component does**
- Aligns transaction fees with stablecoin-denominated payment flows
- Reduces the need for users to hold a separate utility asset
- Connects fee payment to Tempo's stablecoin-first design

**Why it matters**
This is one of the main ways Tempo makes onchain payments feel closer to real payment infrastructure and less like conventional crypto gas management.

### 4.3 Policy and Compliance Hooks

Tempo documentation references policy-oriented protocol components, such as TIP-403-style policy systems.

**What this component does**
- Allows stablecoin and payment flows to connect to policy controls
- Supports structured payment behavior
- Helps align payment primitives with real-world compliance requirements

**Why it matters**
Tempo is clearly not positioning itself as a purely speculative crypto stack. Policy hooks suggest a design meant for payment infrastructure that can interact with regulated financial requirements.

### 4.4 Stablecoin DEX / Exchange Layer

Tempo documentation also references a Stablecoin DEX.

**What this component does**
- Supports exchange and routing between supported stable assets
- Helps applications move between payment assets
- Makes flows more usable when payer and receiver do not use the same stablecoin

**Why it matters**
Exchange primitives are important in payment systems because liquidity and routing often determine whether a flow is actually usable in practice.

### 4.5 How the Asset Layer Connects to the Transaction Layer

This is where the separation between Tempo Transactions and TIP-20 becomes useful:

- Tempo Transactions can reference fee tokens
- batched calls can carry TIP-20 transfers or approvals
- delegated access can impose TIP-20 spending limits
- payment flows often settle through TIP-20 assets

So the transaction layer and asset layer are tightly coupled in practice, but they should still be described separately in the architecture.

---

## 5. Wallet and Identity Layer

This layer connects users and applications to the protocol in a usable way. It sits above transactions and assets because it is how humans and software gain permission to use them safely.

### 5.1 Tempo Wallet

Tempo Wallet is the user-facing account and authorization surface.

**What this component does**
- Manages user identity and access
- Supports account onboarding
- Coordinates passkey-based authentication
- Allows users to fund and use Tempo accounts
- Connects human approval to machine-usable credentials

**How users encounter it**
- A human logs into a wallet flow
- The wallet creates or manages account credentials
- The wallet may approve a session for an app, CLI, or agent

### 5.2 Passkeys / WebAuthn

Passkeys and WebAuthn are a major part of Tempo's account experience.

**What this component does**
- Lets users authenticate with passkey-style credentials
- Provides a friendlier account model than raw private key management
- Supports strong authentication for payment flows

**Why it matters**
Passkeys reduce friction for users and make it easier to bridge modern app authentication with blockchain-native payment execution.

### 5.3 Scoped Session Keys

A session key is a delegated credential that lets an app or agent act within defined boundaries.

**What this component does**
- Grants temporary or limited authority
- Restricts spending scope, time window, or usage pattern
- Allows repeated actions without repeated full user approval

**Why it matters**
Session keys are what make agentic workflows practical. Without them, a user would need to manually approve every machine-driven payment.

### 5.4 Key Manager

A key manager is the service or system that helps organize, issue, or maintain user keys and passkey-linked credentials.

**What this component does**
- Helps manage account-linked signing authority
- Supports passkey-linked account flows
- Enables operational handling of authentication material

**How developers encounter it**
- Usually through official infrastructure or wallet tooling
- Often indirectly, rather than by building it from scratch

---

## 6. Machine Payments Layer

This is the bridge between application requests and settlement. It is where Tempo's machine-commerce story becomes concrete.

### 6.1 HTTP 402 Payment Required

HTTP 402 is the payment-required status code that sits at the heart of Tempo's machine payment story.

**What this component does**
- Signals that a request requires payment
- Returns structured payment requirements to the client
- Allows service access to be negotiated in-band with the request

**Why it matters**
Instead of relying on out-of-band account setup, a service can simply tell a client how to pay for a request.

### 6.2 MPP (Machine Payments Protocol)

MPP is the protocol that turns a payment-required response into a machine-usable payment workflow.

**What this component does**
- Defines how a client interprets payment requirements
- Allows software to pay for a request programmatically
- Supports agent-to-service and machine-to-machine payment flows
- Provides the protocol semantics for payable APIs

**Why it matters**
MPP is the clearest expression of Tempo's AI and machine-commerce strategy. It lets software discover that it must pay, make the payment, and continue the interaction.

### 6.3 Session Payments

A session payment model lets a client establish a payable relationship once and then continue using a service within the session boundaries.

**What this component does**
- Avoids repeated one-off setup for every request
- Supports ongoing access patterns
- Makes repeated paid calls more efficient

### 6.4 Streaming Payments

Streaming payments are the logical extension of session-style access. Instead of paying only once per request, a system can support continuous or incrementally metered usage.

**What this component does**
- Supports continuous service delivery
- Aligns payment flow with real-time or ongoing resource usage
- Makes machine consumption more granular and programmable

---

## 7. Application Layer

The application layer sits at the top of the stack. Tempo does not define one canonical application here. This is where builders create products that use Tempo for payments, settlement, or machine commerce.

### 7.1 User

The user is the human who authorizes activity, funds accounts, and ultimately receives value from the system.

**What this component does**
- Owns or controls funds
- Approves access and payment authority
- Consumes services indirectly through apps or agents

**How it connects to the stack**
- Interacts directly with the wallet and identity layer
- May delegate limited authority to an app or agent
- May never directly touch raw chain mechanics

### 7.2 Agent or App

This is the software acting on the user's behalf. It may be an AI agent, a CLI workflow, a mobile app, a backend service, or an automation layer.

**What this component does**
- Requests services
- Handles payment-required responses
- Uses delegated credentials or session keys
- Coordinates payment and service access

**Why it matters**
This is one of Tempo's most distinctive use cases. The stack is designed so that software can pay for services programmatically instead of depending only on API keys, invoices, or monthly billing accounts.

### 7.3 Paid Service or API

A paid service is any endpoint or system that charges for access.

**What this component does**
- Receives requests from apps or agents
- Returns service responses only after payment conditions are met
- May support one-shot payments, sessions, or continuous billing models

### 7.4 Search, Routing, Intent Matching, and Skill Selection

These components are often discussed around AI agents, but they are best treated as application-specific, not Tempo core.

**What they do**
- Help an agent discover services
- Choose among providers
- Match user intent to a payable service
- Route a request to the correct endpoint

**Why this distinction matters**
They may be built on top of Tempo and can be very important in real products, but they are not the same thing as Tempo's protocol layer.

---

## 8. Infrastructure and Developer Tooling

These components are not always part of the protocol in the narrowest sense, but they are an important part of the complete Tempo platform. They support multiple layers of the stack rather than belonging to only one.

### 8.1 SDKs

Tempo offers SDKs in multiple languages, including TypeScript, Go, Python, and Rust.

**What these components do**
- Let developers connect to Tempo
- Build payment-aware apps
- Interact with wallets, transactions, and machine payment flows
- Reduce the need to build everything from scratch

### 8.2 CLI

The CLI is a practical user and developer interface into the system.

**What this component does**
- Lets users manage wallets and accounts
- Lets developers test payment flows
- Provides a command-line interface for requesting payable services

### 8.3 Explorer

The explorer provides visibility into blocks, transactions, and network activity.

**What this component does**
- Helps users verify what happened on-chain
- Supports debugging and operational visibility
- Gives infrastructure a public transparency layer

### 8.4 Contract Verification

A contract verification service helps developers prove what source code corresponds to deployed contracts.

**What this component does**
- Improves transparency
- Supports contract trust and inspection
- Makes the ecosystem more usable for developers and users

### 8.5 Token List Registry

A token list registry helps wallets and apps understand which tokens should be recognized and how they should be displayed.

**What this component does**
- Improves asset discovery and metadata handling
- Helps applications present stablecoins and supported assets correctly

### 8.6 Fee Sponsor Service

This is the operational service counterpart to protocol-level fee sponsorship.

**What this component does**
- Provides a service implementation for sponsored transaction flows
- Helps apps test and deploy better onboarding experiences

---

## 9. Optional or App-Specific Integrations

Not everything discussed around Tempo should be treated as a first-party protocol component.

### 9.1 Payment Service Providers

A PSP integration may connect Tempo to broader financial workflows.

**Possible roles**
- Fiat on/off ramps
- Merchant settlement paths
- Enterprise payment orchestration

### 9.2 Virtual Cards

Virtual cards may be built on top of Tempo-related payment infrastructure, but they are best treated as an application or integration pattern, not a protocol primitive.

### 9.3 Escrow Services

Escrow is useful in many payment systems, but it is a business logic layer, not automatically part of Tempo's core stack.

### 9.4 TEE or Secure Execution

Trusted execution environments may matter in certain agent systems, but they should be considered a security architecture choice above the base Tempo protocol unless explicitly documented as a native Tempo component.

---

## 10. End-to-End Example Flow

A typical Tempo-style machine payment flow can be understood like this:

1. Tempo mainnet provides the execution and settlement base.
2. Tempo Transactions provide the transaction model used to express payment actions.
3. TIP-20 assets provide the stablecoin value being transferred or used for fees.
4. The wallet creates or links the user's credentials.
5. The user grants an app or agent a scoped session.
6. The agent requests a paid service.
7. The service responds with HTTP 402 and payment requirements.
8. The client uses MPP to construct and deliver payment.
9. The transaction settles on Tempo.
10. The service verifies payment and returns the result.
11. The user receives the output.

This flow shows why Tempo should be understood as a stack rather than a single product.

---

## 11. Bottom Line

Tempo's architecture is best understood as a layered payment system:

- **Tempo mainnet** is the settlement and execution base
- **Tempo Transactions** are the transaction layer
- **TIP-20** is the asset and stablecoin layer
- **Wallets, passkeys, and session keys** are the identity and authorization layer
- **MPP and 402-based flows** are the machine payments layer
- **Agents, apps, and paid services** are the application layer

The most important architectural point is that Tempo treats payment logic, user-friendly authorization, and machine-driven access as first-class system design goals.

The most important structural point is that **Tempo Transactions and TIP-20 should be described as different layers**:

- Tempo Transactions define how the system acts
- TIP-20 defines what payment assets move through the system
