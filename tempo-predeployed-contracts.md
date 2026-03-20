# Tempo Predeployed System Contracts

## Overview

Tempo includes a set of **predeployed system contracts** that form the protocol-level infrastructure for payments, token operations, fee management, exchange, and compliance.

Unlike application-deployed contracts, these contracts are part of Tempo's protocol surface. They exist at deterministic addresses from genesis and are expected to be used by wallets, SDKs, and applications building on Tempo.

---

## System Contracts

These are the core protocol contracts that power Tempo's payment features.

| Contract | Address | Purpose |
|---|---|---|
| TIP-20 Factory | `0x20fc000000000000000000000000000000000000` | Create new TIP-20 tokens |
| Fee Manager | `0xfeec000000000000000000000000000000000000` | Handle fee payments and conversions |
| Stablecoin DEX | `0xdec0000000000000000000000000000000000000` | Enshrined DEX for stablecoin swaps |
| TIP-403 Registry | `0x403c000000000000000000000000000000000000` | Transfer policy registry |
| pathUSD | `0x20c0000000000000000000000000000000000000` | First stablecoin deployed; default fee fallback |
| Account Keychain | `0xAAAAAAAA00000000000000000000000000000000` | Access key management precompile |
| Nonce Precompile | `0x4E4F4E4345000000000000000000000000000000` | 2D nonce tracking for parallelizable transactions |

---

## Address Design and Payment Lane Classification

The contract addresses are not arbitrary. Tempo uses a **deterministic address scheme** that has protocol-level significance.

### TIP-20 Payment Prefix

The payment lane specification classifies transactions as **payment transactions** when the target address starts with the prefix:

```text
0x20c0000000000000000000000000
```

This means:

- TIP-20 tokens created through the TIP-20 Factory receive deterministic addresses starting with this prefix
- The protocol can identify payment transactions from transaction data alone, without state lookups
- Payment transactions are routed into the **payment lane**, which has dedicated blockspace (~94% of total capacity)
- `pathUSD` sits at `0x20c0000000000000000000000000000000000000`, the base of this address space

This address-based classification is what enables Tempo's payment lane to work efficiently as a stateless transaction classification mechanism.

### Other Address Patterns

Other system contracts use memorable hex prefixes:

- `0x20fc` — TIP-20 Factory ("20" for TIP-20, "fc" for factory)
- `0xfeec` — Fee Manager ("fee" prefix)
- `0xdec0` — Stablecoin DEX ("dec" for decentralized exchange)
- `0x403c` — TIP-403 Registry ("403" prefix)
- `0xAAAAAAAA` — Account Keychain (easy-to-remember sentinel)
- `0x4E4F4E4345` — Nonce precompile (ASCII hex for "NONCE")

---

## What Each Contract Does

### TIP-20 Factory

The entry point for creating new TIP-20 tokens. All TIP-20 tokens are created by calling `createToken` on this contract. The factory ensures tokens receive deterministic addresses within the payment prefix address space.

### Fee Manager

Manages the fee lifecycle:

- determines fee tokens based on the preference hierarchy
- collects maximum fees before transaction execution
- refunds unused gas after execution
- coordinates fee conversion through the Fee AMM
- tracks validator fee preferences
- enables fee claiming via `distributeFees()`

Accounts can set their default fee token preference by calling `setUserToken` on this contract. Validators set their preferred receiving token with `setValidatorToken`.

### Stablecoin DEX

The enshrined stablecoin exchange for trading between TIP-20 stablecoins. Operates as an **onchain orderbook** with price-time priority. Currently scoped to USD-denominated TIP-20 tokens.

Uses a **quote-token tree** structure where each token designates a single quote token, creating a cycle-free graph with exactly one route between any two tokens. This design reduces routing ambiguity and liquidity fragmentation.

### TIP-403 Registry

The shared transfer-authorization registry. Stores whitelist and blacklist policies that TIP-20 tokens reference during transfers. Policies can be shared across multiple tokens.

Built-in policies:
- `policyId = 0` — always reject
- `policyId = 1` — always allow (default for new tokens)

### pathUSD

Tempo's first predeployed stablecoin. Serves as the **default fee fallback** when no other fee-token preference is set. Also acts as a natural routing anchor in the quote-token tree of the Stablecoin DEX.

### Account Keychain

Precompile that manages authorized access keys for accounts. Stores key metadata including signature type, expiry timestamps, and per-TIP-20 spending limits. Enforces the root-key / access-key authorization hierarchy.

### Nonce Precompile

Manages the 2D nonce system for Tempo Transactions. Stores user nonce keys (1–N) while protocol nonces (key 0) are stored in standard account state.

---

## Standard Utility Contracts

Tempo also predeployes popular Ethereum utility contracts for developer convenience:

| Contract | Address | Purpose |
|---|---|---|
| Multicall3 | `0xcA11bde05977b3631167028862bE2a173976CA11` | Batch multiple calls in one transaction |
| CreateX | `0xba5Ed099633D3B313e4D5F7bdc1305d3c28ba5Ed` | Deterministic contract deployment |
| Permit2 | `0x000000000022d473030f116ddee9f6b43ac78ba3` | Token approvals and transfers |
| Arachnid Create2 Factory | `0x4e59b44847b379578588920cA78FbF26c0B4956C` | CREATE2 deployment proxy |
| Safe Deployer | `0x914d7Fec6aaC8cd542e72Bca78B30650d45643d7` | Safe deployer contract |

---

## Accessing ABIs

Contract ABIs are available through the SDK:

```typescript
import { Abis } from 'viem/tempo'

const tip20Abi = Abis.tip20
const tip20FactoryAbi = Abis.tip20Factory
const stablecoinDexAbi = Abis.stablecoinDex
const feeManagerAbi = Abis.feeManager
const feeAmmAbi = Abis.feeAmm
```

---

## Why This Matters

The predeployed contract set is significant because it shows Tempo is a **platform**, not just a protocol specification:

- Applications have standard, deterministic addresses to interact with
- Wallets can hardcode addresses for core operations
- The payment lane classification depends on the deterministic address scheme
- Developers do not need to discover or choose between competing implementations of core infrastructure

---

## References

- Predeployed Contracts: https://docs.tempo.xyz/quickstart/predeployed-contracts
- TIP-20 Specification: https://docs.tempo.xyz/protocol/tip20/spec
- Fee Specification: https://docs.tempo.xyz/protocol/fees/spec-fee
- Stablecoin DEX: https://docs.tempo.xyz/protocol/exchange
- TIP-403 Specification: https://docs.tempo.xyz/protocol/tip403/spec
- Account Keychain: https://docs.tempo.xyz/protocol/transactions/AccountKeychain
