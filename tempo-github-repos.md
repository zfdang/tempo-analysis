# Tempo GitHub Repository Guide

This document summarizes the most important public repositories in the `tempoxyz` GitHub organization, what each repository is for, who should care about it, and how to get started.

## Quick Orientation

If you only want to know where to start:

- To understand **what Tempo is**: start with `tempo` and `docs`
- To **use the wallet or CLI**: start with `wallet`
- To build **machine payments / AI agent payments**: start with `mpp`, `pympp`, and `mpp-rs`
- To build with **SDKs**: start with `tempo-ts` or `tempo-go`
- To do **smart contract development**: start with `tempo-foundry` and `tempo-std`
- To inspect official supporting services: start with `tempo-apps`
- If you do not know where to ask a question: use `tempo-support`

---

## 1. Core Protocol and Network

### `tempoxyz/tempo`

**What it is**  
The main Tempo protocol repository. This is the core blockchain implementation and the best place to understand Tempo at the network and protocol level.

**What it does**
- Implements the Tempo blockchain
- Contains payment-oriented protocol features
- Covers Tempo Transactions and related core behavior
- Includes chain-level payment primitives such as fee logic and token-related protocol features
- Supports node and protocol-level development

**Who should use it**
- Protocol researchers
- Node operators
- Core contributors
- Developers who need to understand the chain itself

**How users should approach it**
- Most end users do not need to interact with this repository directly
- App developers usually start with SDKs or the wallet instead
- Use this repo when you need protocol depth, node-level work, or chain implementation details

---

## 2. Official Documentation

### `tempoxyz/docs`

**What it is**  
The source repository for the official Tempo documentation.

**What it does**
- Powers the documentation site
- Contains protocol specifications
- Includes getting started guides
- Covers SDKs, tooling, transactions, tokens, and other developer-facing topics

**Who should use it**
- Everyone
- This is the best first stop before diving into source code

**How users should approach it**
- Read the docs site first
- Use the repository if you want to inspect or contribute to the documentation itself
- This is the best place for onboarding and conceptual understanding

---

## 3. Wallet and CLI

### `tempoxyz/wallet`

**What it is**  
The Tempo wallet repository, positioned as a command-line wallet and HTTP client with native machine payments support.

**What it does**
- Provides the CLI wallet experience
- Manages local keys and wallet identity
- Supports passkey login and session authorization
- Lets users request paid services directly
- Handles `402 Payment Required` responses in a native flow
- Supports session and streaming payment flows

**Who should use it**
- Users who want to directly try Tempo
- Developers who want an end-to-end payment flow without building everything from scratch
- Agent builders who want a practical payment client

**How users should approach it**
- Install the CLI
- Log in with the wallet flow
- Fund an account
- Use the CLI to call paid services
- This is the most product-like repository for hands-on usage

---

## 4. Machine Payments Protocol

### `tempoxyz/mpp`

**What it is**  
The main repository for the Machine Payments Protocol.

**What it does**
- Hosts the protocol-facing documentation and quickstart material
- Defines and explains machine-to-machine payment flows
- Acts as an entry point for service directory and discovery concepts
- Helps developers understand the HTTP payment model behind Tempo's machine payment story

**Who should use it**
- Developers building machine-payable APIs
- Teams exploring AI agent payment flows
- Anyone trying to understand Tempo's machine commerce layer

**How users should approach it**
- Read this repo first if your focus is agent payments
- Use it to understand how payment requests and service access are meant to work
- Treat this as the conceptual and protocol entry point rather than the end-user tool

### `tempoxyz/mpp-specs`

**What it is**  
The repository for the underlying protocol specifications.

**What it does**
- Contains standards-oriented protocol definitions
- Captures the protocol in a more formal specification style
- Supports compatible implementations

**Who should use it**
- Standards-minded readers
- Protocol implementers
- Teams building interoperable services

**How users should approach it**
- Start here if you want the specification, not just the implementation or overview
- Best for protocol review or standards-level work

### `tempoxyz/mpp-rs`

**What it is**  
A Rust SDK for MPP.

**What it does**
- Enables Rust-based machine payment integrations

**Who should use it**
- Rust developers building clients, servers, or agents that need machine payments

**How users should approach it**
- Pair it with the main `mpp` repository so you understand the protocol while implementing it

### `tempoxyz/pympp`

**What it is**  
A Python SDK for the Machine Payments Protocol.

**What it does**
- Lets Python services expose paid endpoints
- Lets Python clients pay to consume services
- Includes examples for practical integration

**Who should use it**
- Python backend developers
- Builders of Python APIs, agent backends, or machine-payable services
- Teams that want the fastest path to prototyping MPP flows in Python

**How users should approach it**
- Install the package
- Use the server-side helpers to make API routes payable
- Use the client helpers to access paid services
- This is one of the most practical repos for service integration

---

## 5. SDKs for App Developers

### `tempoxyz/tempo-ts`

**What it is**  
The TypeScript tooling and SDK repository for Tempo.

**What it does**
- Provides TypeScript-side tooling for working with Tempo
- Supports application and server-side integration patterns

**Who should use it**
- TypeScript developers
- Frontend teams
- Node.js backends integrating with Tempo

**How users should approach it**
- Start here if your stack is TypeScript
- Use it alongside the official docs and examples
- Best for app integration rather than protocol research

### `tempoxyz/tempo-go`

**What it is**  
The Go SDK for the Tempo blockchain.

**What it does**
- Provides RPC client functionality
- Includes signing and transaction-building tools
- Supports sending transactions and building integrations in Go

**Who should use it**
- Go backend developers
- Infrastructure engineers building Tempo integrations
- Teams building payment services in Go

**How users should approach it**
- Use this if your backend stack is Go
- Follow its quick start and examples
- Best for direct chain integration in Go

### `tempoxyz/pytempo`

**What it is**  
A proof-of-concept Python client for Tempo.

**What it does**
- Experiments with Python-side access to Tempo

**Who should use it**
- Developers exploring Python integrations at an early stage
- People who want to evaluate experimental Python access

**How users should approach it**
- Treat this as a proof of concept rather than the main supported path
- For machine payments in Python, `pympp` is usually the more practical starting point

---

## 6. Smart Contract Development

### `tempoxyz/tempo-foundry`

**What it is**  
A Tempo-oriented Foundry distribution or integration for smart contract development.

**What it does**
- Adapts Foundry workflows to Tempo-specific protocol behavior
- Helps contract developers build with Tempo in a more native way

**Who should use it**
- Solidity developers
- Smart contract teams building on Tempo
- Builders who already prefer Foundry

**How users should approach it**
- Start here if you are building contracts for Tempo and already use Foundry
- This is the right place for Tempo-specific development workflows

### `tempoxyz/tempo-std`

**What it is**  
The Tempo standard library for contracts and developer utilities.

**What it does**
- Provides Tempo-specific interfaces and libraries
- Supports Foundry-based contract development

**Who should use it**
- Smart contract developers building on Tempo
- Teams that want reusable Tempo-native abstractions

**How users should approach it**
- Use it together with `tempo-foundry`
- Install it into contract projects to access Tempo-specific interfaces and helpers

---

## 7. Official Apps and Supporting Infrastructure

### `tempoxyz/tempo-apps`

**What it is**  
The monorepo for Tempo's supporting applications and service infrastructure.

**What it does**
- Contains the explorer
- Contains fee sponsorship services
- Contains token list services
- Contains contract verification services
- Contains key management services

**Who should use it**
- Developers who want to understand how official supporting apps are structured
- Teams that want reference implementations for surrounding infrastructure
- Builders who want to inspect or adapt official app-layer services

**How users should approach it**
- End users usually do not need to clone this repository
- Developers should use it as a reference for platform services
- This repo is especially valuable for understanding the ecosystem around the protocol

---

## 8. Examples and Integration Helpers

### `tempoxyz/examples`

**What it is**  
A repository of TypeScript examples built on Tempo.

**What it does**
- Shows how to use Tempo through practical examples
- Helps developers learn by running working code

**Who should use it**
- Developers who learn best from examples
- Teams trying to move quickly from theory to working code

**How users should approach it**
- Use this alongside the docs and TypeScript SDK
- Start here if you want a concrete path to first integration

### `tempoxyz/agent-skills`

**What it is**  
A repository oriented toward agent-related integrations and skills.

**What it does**
- Supports agent workflow integration for Tempo-related use cases

**Who should use it**
- Teams building AI agents or agent tooling
- Developers who want reusable Tempo-related skills in an agent environment

**How users should approach it**
- Focus on this repo if your primary use case is AI agent integration
- It is more specialized than the core protocol and wallet repositories

---

## 9. Support and Questions

### `tempoxyz/tempo-support`

**What it is**  
The support and triage repository for Tempo questions.

**What it does**
- Provides a place to ask for help
- Helps route questions to the correct repository
- Serves as a general support entry point

**Who should use it**
- Anyone who does not know where a question belongs
- New users and new developers
- Contributors needing help navigating the project structure

**How users should approach it**
- Check the docs first
- If you still are not sure where to file an issue, use this repo
- Use private channels rather than public issues for security-sensitive reports

---

## 10. Repositories Most Users Can Ignore at First

The organization also contains a number of repositories that appear to be forks, experiments, supporting utilities, or internal infrastructure. These may include custom Foundry or Reth variants, test tools, proxies, and other development support repositories.

Examples include repositories with names such as:
- `foundry`
- `foundry-3`
- `foundry-4`
- `foundry-5`
- `foundry-tempo-pr`
- `reth`
- `reth-2`
- `reth-3`
- `reth-4`
- `metrics-derive`
- `rpc-tester`
- `cf-template-proxy`
- `mpp-proxy-cf`
- `incur-rs`
- `changelogs`

Most users and most application developers do not need to start with these. They may be relevant for deeper infrastructure work, internal experimentation, or protocol-adjacent engineering, but they are not the primary entry points.

---

## Recommended Starting Paths

### If you are a normal user or just want to try Tempo
Start with:
1. `docs`
2. `wallet`

### If you are building AI agents or machine-payable services
Start with:
1. `mpp`
2. `wallet`
3. `pympp` or `mpp-rs`

### If you are a TypeScript developer
Start with:
1. `docs`
2. `tempo-ts`
3. `examples`

### If you are a Go developer
Start with:
1. `docs`
2. `tempo-go`

### If you are a smart contract developer
Start with:
1. `docs`
2. `tempo-foundry`
3. `tempo-std`

### If you are unsure where to ask a question
Start with:
1. `tempo-support`

---

## Short Repo Map

**Core**
- `tempo`
- `docs`
- `wallet`
- `mpp`

**Main SDKs and developer tooling**
- `tempo-ts`
- `tempo-go`
- `pympp`
- `mpp-rs`
- `tempo-foundry`
- `tempo-std`

**Official infrastructure**
- `tempo-apps`

**Support and examples**
- `examples`
- `tempo-support`
- `agent-skills`

**Experimental or lower-priority entry points**
- `pytempo`
- various `reth` / `foundry` forks and support utilities

---

## Bottom Line

Tempo's GitHub organization is broader than a single blockchain repository. It spans:

- the core payment-oriented network
- wallet and CLI tooling
- machine payment protocols
- SDKs in multiple languages
- smart contract tooling
- official supporting applications
- examples and support channels

For most people, the best entry point is not the deepest protocol repo. It is usually one of these four:
- `docs`
- `wallet`
- `mpp`
- the SDK for your preferred language

That path gets you productive much faster.
