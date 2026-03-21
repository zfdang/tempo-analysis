# Tempo Analysis

This repository contains technical analysis of the Tempo protocol and ecosystem.


```
Tempo
├── L1 Network
│   ├── Simplex BFT consensus (~600ms blocks)
│   └── Payment lanes (~94% payment / ~6% general)
├── 0x76 Transaction Type
│   ├── Passkeys / WebAuthn signing
│   ├── 2D nonces & batch calls
│   ├── Fee sponsorship
│   ├── Access keys & delegation
│   └── Account Keychain
├── Asset Layer
│   ├── TIP-20 (stablecoin token standard)
│   ├── TIP-20 Rewards
│   ├── TIP-403 (compliance & policy registry)
│   └── pathUSD (native quote token)
├── Fee & Exchange Layer
│   ├── USD-denominated fees (attodollars)
│   ├── Fee AMM
│   └── Stablecoin DEX (enshrined orderbook)
├── Wallet / CLI / SDKs
├── MPP (HTTP 402 machine payments)
└── Infra Apps
    ├── Explorer & Contract Verification
    ├── Tokenlist Registry
    └── Key Manager & Fee Payer
```

## Recommended Reading Order

### Context and Overview

1. [tempo-overview.md](docs/tempo-overview.md)  
   What Tempo is, what product areas it includes, and the main ideas behind the stack.

3. [tempo-architecture.md](docs/tempo-architecture.md)  
   Mermaid diagrams for the layered architecture, product overview, and agent payment flow.

4. [tempo_protocol_components_guide.md](docs/tempo_protocol_components_guide.md)  
   A bottom-up explanation of the stack from network and execution up to applications.

### Network and Execution Layer

5. [tempo-network-execution-layer.md](docs/tempo-network-execution-layer.md)  
   How Tempo extends Ethereum at the network and execution layer, and what those changes enable.

6. [tempo-predeployed-contracts.md](docs/tempo-predeployed-contracts.md)  
   System contract addresses, the TIP-20 payment prefix, address design, and standard utilities.

### Transaction Layer

7. [tempo-0x76-transaction-type.md](docs/tempo-0x76-transaction-type.md)  
   The Tempo `0x76` typed transaction and its protocol-native account and payment features.

### Asset and Stablecoin Layer

8. [tip-20-vs-erc-20.md](docs/tip-20-vs-erc-20.md)  
   How TIP-20 differs from ERC-20 and why Tempo treats stablecoins as a first-class asset.

9. [tempo-tip20-rewards.md](docs/tempo-tip20-rewards.md)  
   The built-in, opt-in reward distribution system for TIP-20 token holders.

10. [tip-403-detailed-guide.md](docs/tip-403-detailed-guide.md)  
    The policy and compliance layer (whitelist/blacklist registry) for TIP-20 tokens.

### Fees and Exchange

11. [tempo-fees-and-fee-amm.md](docs/tempo-fees-and-fee-amm.md)  
    Tempo's fee model, stablecoin fee payment, validator settlement, the Fee AMM, and TIP-1010 gas parameters.

12. [tempo-stablecoin-dex-and-fx.md](docs/tempo-stablecoin-dex-and-fx.md)  
    The enshrined stablecoin exchange, quote-token routing, orderbook model, and current FX scope.

### Wallet and Identity Layer

13. [tempo-wallet-vs-eoa-vs-smart-contract-wallet.md](docs/tempo-wallet-vs-eoa-vs-smart-contract-wallet.md)  
    A mental model for how Tempo wallets relate to EOAs and smart contract wallets.

14. [tempo-accounts-passkeys-and-access-keys.md](docs/tempo-accounts-passkeys-and-access-keys.md)  
    Tempo's account layer: passkeys, connected wallets, access keys, and the Account Keychain.

### Machine Payments Layer

15. [mpp_overview_participants_architecture.md](docs/mpp_overview_participants_architecture.md)  
    Who is driving MPP, the current public ecosystem participants, protocol status, and the high-level architecture.

16. [tempo-mpp-architecture-and-modules.md](docs/tempo-mpp-architecture-and-modules.md)  
    The architecture and module breakdown of Tempo's Machine Payments Protocol.

17. [tempo-mpp-vs-x402.md](docs/tempo-mpp-vs-x402.md)  
    A comparison between Tempo's MPP approach and `x402`.

### Application Layer and Developer Surface

18. [tempo-application-layer-overview.md](docs/tempo-application-layer-overview.md)  
    How payments, issuance, exchange, and machine commerce sit at the application layer.

19. [tempo-github-repos.md](docs/tempo-github-repos.md)  
    A guide to Tempo's public repositories and what each one does.

## Coverage Map

Reading the list above in order covers:

- the overall Tempo product story and layered architecture
- the protocol stack from network to application layer
- system contracts and address architecture
- transactions, accounts, passkeys, and delegated access keys
- assets: TIP-20, rewards, and TIP-403 compliance policies
- fees, stablecoin exchange, and cross-stablecoin routing
- machine payments, MPP ecosystem participants and status, MPP vs x402, and agentic commerce
- application-layer design and the public repo surface
