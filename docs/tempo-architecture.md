# Tempo Architecture Notes

This document contains three Mermaid diagrams for understanding Tempo:
1. Layered architecture
2. Simplified product overview
3. Agent payment sequence flow

---

## 1. Layered Architecture

```mermaid
flowchart TB
  subgraph APP["Application Layer (app-specific)"]
    U["User"]
    AG["Agent / App"]
    SRV["Paid Service / API"]
    SEARCH["Service Search / Routing"]
    INTENT["Intent Matching"]
    SKILL["Skill Selection"]
  end

  subgraph ID["Wallet / Identity Layer"]
    WALLET["Tempo Wallet"]
    CLI["Tempo CLI"]
    PASSKEY["Passkeys / WebAuthn"]
    SESSION["Scoped Session Keys"]
    KEYMGR["Key Manager"]
  end

  subgraph MPPL["Machine Payments Layer"]
    HTTP402["HTTP 402 Payment Required"]
    MPP["MPP"]
    STREAM["Session / Streaming Payments"]
  end

  subgraph PROTO["Tempo Protocol Layer"]
    TX["Tempo Transactions"]
    BATCH["Batch Calls"]
    SCHEDULE["Scheduled Payments"]
    SPONSOR["Fee Sponsorship"]
    TIP20["TIP-20 Stablecoin Standard"]
    FEES["Stablecoin Fees"]
    DEX["Stablecoin DEX / Swap"]
    POLICY["Policy / Compliance Hooks"]
  end

  subgraph NET["Network Layer"]
    MAINNET["Tempo Mainnet / L1"]
    EXEC["EVM-compatible Execution"]
    LANES["Payment-focused Blockspace / Lanes"]
  end

  subgraph INFRA["Infra / Developer Tooling"]
    SDK["SDKs: TS / Go / Python / Rust"]
    FOUNDRY["Tempo Foundry / Stdlib"]
    EXPLORER["Explorer"]
    VERIFY["Contract Verification"]
    TOKENLIST["Token List Registry"]
    FEEPAYER["Fee Sponsor Service"]
  end

  subgraph OPT["Optional Integrations (not Tempo core)"]
    PSP["PSP / Stripe-like Integration"]
    VCARD["Virtual Card"]
    ESCROW["Escrow"]
    TEE["TEE / Secure Execution"]
  end

  U --> AG
  AG --> SEARCH
  SEARCH --> INTENT
  INTENT --> SKILL
  SKILL --> SRV

  U --> WALLET
  WALLET --> PASSKEY
  PASSKEY --> SESSION
  CLI --> SESSION
  KEYMGR --> SESSION
  AG --> CLI

  SRV --> HTTP402
  AG --> MPP
  HTTP402 --> MPP
  MPP --> STREAM

  SESSION --> TX
  MPP --> TX
  TX --> BATCH
  TX --> SCHEDULE
  TX --> SPONSOR
  TX --> TIP20
  TIP20 --> FEES
  TIP20 --> POLICY
  TIP20 --> DEX

  TX --> MAINNET
  MAINNET --> EXEC
  MAINNET --> LANES

  SDK --> TX
  SDK --> MPP
  FOUNDRY --> TX
  EXPLORER --> MAINNET
  VERIFY --> MAINNET
  TOKENLIST --> TIP20
  FEEPAYER --> SPONSOR

  AG -.-> PSP
  PSP -.-> VCARD
  PSP -.-> ESCROW
  AG -.-> TEE
  PSP -.-> MAINNET
```

---

## 2. Simplified Product Overview

```mermaid
flowchart TB
  subgraph A["Apps"]
    USER["User"]
    AGENT["Agent / App"]
    SERVICE["Paid API / Service"]
  end

  subgraph B["Wallet & Auth"]
    W["Tempo Wallet / CLI"]
    P["Passkeys"]
    S["Session Keys"]
  end

  subgraph C["Payments"]
    M["MPP / HTTP 402"]
    ST["Streaming / Session Payments"]
  end

  subgraph D["Protocol"]
    T["Tempo Transactions"]
    TIP["TIP-20"]
    F["Fee Sponsorship"]
    X["Stablecoin DEX"]
  end

  subgraph E["Network"]
    N["Tempo Mainnet"]
  end

  subgraph F2["Infra"]
    I["Explorer / Verification / Tokenlist / SDKs"]
  end

  USER --> AGENT
  USER --> W
  W --> P
  P --> S
  AGENT --> SERVICE
  SERVICE --> M
  AGENT --> M
  M --> ST
  S --> T
  M --> T
  T --> TIP
  T --> F
  TIP --> X
  T --> N
  I --> N
```

---

## 3. Agent Payment Sequence

```mermaid
sequenceDiagram
  participant U as User
  participant W as Tempo Wallet
  participant A as Agent / CLI
  participant S as Paid Service
  participant M as MPP / HTTP 402
  participant T as Tempo Network

  U->>W: Approve agent usage
  W->>A: Issue scoped session key
  A->>S: Request service
  S-->>A: HTTP 402 and payment requirements
  A->>M: Build machine payment
  M->>T: Submit payment transaction
  T-->>M: Payment settled
  M-->>S: Proof or confirmation
  S-->>A: Return result or stream output
  A-->>U: Deliver response
```

---

## 4. Architecture vs. Implementation Mapping

The theoretical layered architecture described above maps perfectly to the physical structure of Tempo's open-source repositories on GitHub. Tempo strongly enforces its modular design by mapping components cleanly into separate repositories.

| Architecture Layer | Physical GitHub Repository | Primary Language(s) | Purpose / Implementation Context |
| :--- | :--- | :--- | :--- |
| **Application Layer** | `tempoxyz/agent-skills`<br>`tempoxyz/examples` | **TypeScript**, **Python** | App-specific workflows, skill selection, and AI agent execution integration examples. |
| **Machine Payments Layer (MPP)** | `tempoxyz/mpp`<br>`tempoxyz/mpp-specs`<br>`tempoxyz/pympp`<br>`tempoxyz/mpp-rs` | **TypeScript**, **Python**, **Rust** | Protocol standards and multi-language SDKs focused on handling HTTP 402 payment cycles and sessions. |
| **Wallet / Identity Layer**| `tempoxyz/wallet` | **TypeScript**, **Go** | Implementation of passkey login, WebAuthn abstractions, and handling logic for scoped session keys. |
| **Infra & Developer Tooling** | `tempoxyz/tempo-apps`<br>`tempoxyz/tempo-ts`<br>`tempoxyz/tempo-go` | **TypeScript**, **Go** | Supporting infrastructure (explorer, contract verification, fee sponsorship) and application-level routing SDKs. |
| **Protocol (Contracts & State)**| `tempoxyz/tempo-foundry`<br>`tempoxyz/tempo-std` | **Solidity**, **Rust** | Standard library, precompile interfaces, and custom Foundry tools required to deploy to the transaction and asset environments. |
| **Network & Execution Layer**| `tempoxyz/tempo` | **Rust** | The core node implementation logic for the L1 blockchain itself, including payment lanes and consensus. |