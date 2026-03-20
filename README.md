# Tempo Analysis

This repository contains technical notes about the Tempo protocol and ecosystem.

The documents below are ordered so a reader can move from high-level intuition to protocol details, then to wallet, payment, and application layers.

## Recommended Reading Order

1. [tempo-overview.md](tempo-overview.md)  
   What Tempo is, what product areas it includes, and the main ideas behind the stack.

2. [tempo-architecture.md](tempo-architecture.md)  
   Mermaid diagrams for the layered architecture, product overview, and agent payment flow.

3. [tempo_protocol_components_guide.md](tempo_protocol_components_guide.md)  
   A bottom-up explanation of the stack from network and execution up to applications.

4. [tempo-network-execution-layer.md](tempo-network-execution-layer.md)  
   How Tempo's network and execution layer extends Ethereum, and what those changes enable.

5. [tempo-0x76-transaction-type.md](tempo-0x76-transaction-type.md)  
   The Tempo `0x76` typed transaction and its protocol-native account and payment features.

6. [tip-20-vs-erc-20.md](tip-20-vs-erc-20.md)  
   How TIP-20 differs from ERC-20 and why Tempo treats stablecoins as a first-class asset layer.

7. [tempo-fees-and-fee-amm.md](tempo-fees-and-fee-amm.md)  
   Tempo's fee model, fee-token selection, sponsorship, validator settlement, and the Fee AMM.

8. [tip-403-detailed-guide.md](tip-403-detailed-guide.md)  
   The policy and compliance layer used by TIP-20 tokens.

9. [tempo-stablecoin-dex-and-fx.md](tempo-stablecoin-dex-and-fx.md)  
   The enshrined stablecoin exchange layer, quote-token routing, and Tempo's current FX model.

10. [tempo-wallet-vs-eoa-vs-smart-contract-wallet.md](tempo-wallet-vs-eoa-vs-smart-contract-wallet.md)  
   A mental model for how Tempo wallets relate to EOAs and smart contract wallets.

11. [tempo-accounts-passkeys-and-access-keys.md](tempo-accounts-passkeys-and-access-keys.md)  
    Tempo's account layer: passkeys, connected wallets, access keys, and the Account Keychain.

12. [tempo-mpp-architecture-and-modules.md](tempo-mpp-architecture-and-modules.md)  
    The architecture and module breakdown of Tempo's Machine Payments Protocol.

13. [tempo-mpp-vs-x402.md](tempo-mpp-vs-x402.md)  
    A comparison between Tempo's MPP approach and `x402`.

14. [tempo-application-layer-overview.md](tempo-application-layer-overview.md)  
    How payments, issuance, exchange, and machine commerce sit at the application layer.

15. [tempo-github-repos.md](tempo-github-repos.md)  
    A guide to Tempo's public repositories and what each one appears to do.

## Coverage Map

If you read the list above in order, you will cover:

- the overall Tempo product story
- the protocol stack from network to application layer
- fees, stablecoins, policies, and exchange
- transactions, accounts, passkeys, and delegated access keys
- machine payments and application-facing usage
- the public repo surface for deeper exploration
