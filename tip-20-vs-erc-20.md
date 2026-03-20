# TIP-20 vs. ERC-20

## Overview

**ERC-20** is the canonical fungible token standard for Ethereum. It defines a common interface for token balances, transfers, allowances, and delegated transfers, making tokens interoperable across wallets, exchanges, and smart contracts.

**TIP-20** is Tempo's native fungible token standard. It is designed for **stablecoins and payment tokens** on Tempo and is **backward compatible with ERC-20-style integrations**, while adding built-in features for payment reconciliation, compliance, operational control, reward distribution, and Tempo-native fee and DEX behavior.

A concise way to think about the relationship is:

- **ERC-20** = general-purpose fungible token standard for Ethereum and EVM ecosystems
- **TIP-20** = payment-focused extension of ERC-20 for Tempo

---

## Executive Summary

TIP-20 keeps the familiar ERC-20 core—`balanceOf`, `transfer`, `approve`, `allowance`, and `transferFrom`—but extends it in several important ways:

- **Memo-aware transfers, mints, and burns**
- **Built-in role-based access control**
- **Pause / unpause operations**
- **Transfer-policy enforcement via TIP-403**
- **Supply caps**
- **Currency metadata and quote-token configuration**
- **Built-in rewards distribution**
- **Tempo-native fee payment and payment-lane integration**
- **Core-protocol implementation via precompiles**

So the main difference is not that TIP-20 replaces ERC-20 semantics; rather, it **specializes ERC-20 for payment and stablecoin issuance on Tempo**.

---

## High-Level Comparison Table

| Dimension | ERC-20 | TIP-20 |
|---|---|---|
| Primary purpose | General-purpose fungible tokens | Stablecoins and payment tokens on Tempo |
| Base compatibility | Native standard | Extends ERC-20 behavior and remains backward compatible for common integrations |
| Core functions | `totalSupply`, `balanceOf`, `transfer`, `approve`, `allowance`, `transferFrom` | All familiar ERC-20-style core functions plus Tempo-specific extensions |
| Memo support | No native memo field | Yes, 32-byte memos on transfers, mints, and burns |
| Administrative controls | Not standardized by ERC-20 itself | Built-in RBAC, pause/unpause, blocked-balance burn, supply caps |
| Compliance layer | Not built in | Built-in integration with TIP-403 transfer policies |
| Rewards | Not part of ERC-20 | Native opt-in rewards distribution |
| Currency metadata | Not part of ERC-20 | Built-in `currency()` field for fiat-denomination context |
| DEX routing metadata | Not part of ERC-20 | Built-in quote-token model for Tempo's Stablecoin DEX |
| Fee payment on the chain | Depends on the chain; ERC-20 tokens do not define gas behavior | TIP-20 tokens integrate with Tempo fee payment; only eligible TIP-20 tokens can be used to pay fees |
| Decimal behavior | `decimals()` is optional in the standard | `decimals()` is standardized to return **6** |
| Implementation model | Contract-defined by each issuer | Built-in optimized token implementation via Tempo precompiles |

---

## What ERC-20 Standardizes

ERC-20 defines a standard interface for fungible tokens on Ethereum. At its core, it standardizes:

- token metadata such as `name`, `symbol`, and optionally `decimals`
- total supply tracking
- balance queries
- direct transfers
- approvals and allowances
- delegated transfers via `transferFrom`
- `Transfer` and `Approval` events

Its strength is simplicity and ecosystem portability. A wallet or dApp that understands ERC-20 can usually integrate any ERC-20 token with minimal custom logic.

However, ERC-20 deliberately does **not** standardize many operational requirements that matter for payment issuers, including:

- transfer memos
- issuer permissions and role separation
- transfer whitelists / blacklists
- pause controls
- rewards distribution
- payment-specific metadata
- fee-token behavior

That missing functionality is where TIP-20 adds value.

---

## What TIP-20 Adds on Top of ERC-20

### 1. Transfer memos

TIP-20 adds first-class memo support through functions such as:

- `transferWithMemo`
- `transferFromWithMemo`
- `mintWithMemo`
- `burnWithMemo`

The memo is a fixed **32-byte** field. This is especially useful for:

- invoice IDs
- payment references
- reconciliation IDs
- treasury and settlement workflows

ERC-20 has no equivalent native memo field.

---

### 2. Built-in role-based access control

TIP-20 includes a built-in RBAC system with roles such as:

- `ISSUER_ROLE`
- `PAUSE_ROLE`
- `UNPAUSE_ROLE`
- `BURN_BLOCKED_ROLE`

This gives issuers standardized operational control without having to bolt on custom access-control logic to each token contract.

ERC-20 by itself does not standardize any issuer-role system.

---

### 3. Pause / unpause controls

TIP-20 supports native emergency controls:

- `pause()`
- `unpause()`

For stablecoin issuers and payment operators, this is operationally important. It allows token movement to be halted under defined authority in emergency situations.

ERC-20 does not include pause behavior in the standard.

---

### 4. Compliance and transfer-policy enforcement

TIP-20 integrates with **TIP-403 transfer policies**, allowing tokens to enforce authorization rules on senders and recipients.

That enables policy models such as:

- allowlists
- blocklists
- regulated transfer rules
- shared policy registries across multiple tokens

In contrast, ERC-20 does not define a built-in compliance or policy layer. Issuers that need compliance must implement custom logic or adopt separate standards and modules.

---

### 5. Supply caps and operational controls

TIP-20 includes configurable supply caps and administrative controls, making it easier to support issuer-controlled monetary operations with standard behavior.

This is useful for:

- capped issuance
- permissioned minting
- managed redemption
- operational risk controls

ERC-20 does not standardize supply-cap behavior.

---

### 6. Rewards distribution

TIP-20 includes a built-in, opt-in rewards mechanism for token holders. Rewards can be distributed proportionally to opted-in holders without requiring a separate staking contract.

This is a meaningful difference:

- ERC-20 usually requires a **separate rewards or staking contract**
- TIP-20 can support **native reward distribution** as part of the token standard and Tempo's integrated model

This matters for interest-bearing stablecoins, treasury-sharing arrangements, and issuer-managed yield distribution.

---

### 7. Currency declaration and quote-token behavior

TIP-20 introduces explicit payment-oriented token metadata, including:

- `currency()`
- `quoteToken()`
- `nextQuoteToken()`

The `currency` field represents the fiat denomination or real-world reference currency, such as:

- `USD`
- `EUR`
- `GBP`

This is distinct from token symbol. For example:

- symbol might be `USDC`
- currency should be `USD`

That distinction matters for routing, pricing, and DEX integration on Tempo.

ERC-20 has no equivalent built-in concept.

---

### 8. Tempo-native fee payment and payment lanes

TIP-20 is deeply integrated with Tempo's payment-oriented chain design.

According to Tempo's documentation:

- only **TIP-20 tokens** can be used to pay transaction fees on Tempo
- only **USD-denominated TIP-20 tokens** are currently eligible for fee payment
- TIP-20 payment transactions can access Tempo's **dedicated payment lanes**, which reserve blockspace for payment traffic

This is a chain-level integration, not just a token-interface difference.

ERC-20 does not define or guarantee anything like this, because ERC-20 is only a token standard, not a chain-native payment architecture.

---

### 9. Standardized decimals

In ERC-20, `decimals()` is an **optional** metadata method.

In TIP-20, `decimals()` is standardized and documented to **always return 6**.

This is a subtle but important standardization choice. It reduces ambiguity and aligns better with stablecoin and payment use cases where six-decimal formatting is common.

---

### 10. Core-protocol implementation via precompiles

TIP-20 is not just "an ERC-20 contract with extra methods." Tempo's specification describes TIP-20 as a **suite of precompiles** providing a built-in optimized token implementation in the core protocol.

That gives TIP-20 a different implementation model from typical ERC-20 deployments:

- **ERC-20**: each token issuer deploys and maintains its own contract implementation
- **TIP-20**: token behavior is standardized more deeply in the protocol via Tempo's built-in implementation path

This is one reason Tempo can offer more consistent token behavior across issuers.

---

## Interface Comparison

### ERC-20 core interface

Typical ERC-20 includes:

- `name()`
- `symbol()`
- `decimals()` *(optional)*
- `totalSupply()`
- `balanceOf(address)`
- `transfer(address,uint256)`
- `allowance(address,address)`
- `approve(address,uint256)`
- `transferFrom(address,address,uint256)`

Events:

- `Transfer`
- `Approval`

---

### TIP-20 core and extended interface

TIP-20 includes ERC-20-style functions and extends them with:

**Memo operations**
- `transferWithMemo(address,uint256,bytes32)`
- `transferFromWithMemo(address,address,uint256,bytes32)`
- `mintWithMemo(address,uint256,bytes32)`
- `burnWithMemo(uint256,bytes32)`

**Administrative and policy functions**
- `pause()`
- `unpause()`
- `changeTransferPolicyId(uint64)`
- `setSupplyCap(uint256)`
- `burnBlocked(address,uint256)`

**DEX / currency configuration**
- `currency()`
- `quoteToken()`
- `nextQuoteToken()`
- `setNextQuoteToken(...)`
- `completeQuoteTokenUpdate()`

**Role management**
- `grantRole(bytes32,address)`
- `revokeRole(bytes32,address)`
- `renounceRole(bytes32)`
- `setRoleAdmin(bytes32,bytes32)`

**Additional state queries**
- `paused()`
- `supplyCap()`
- `transferPolicyId()`

**Rewards-related behavior**
- reward configuration and reward distribution primitives in the broader TIP-20 / TIP-20 Rewards model

---

## Practical Meaning for Developers

### When ERC-20 is enough

Use ERC-20 when you want:

- a standard fungible token
- broad Ethereum / EVM compatibility
- minimal token logic
- custom operational behavior implemented separately
- maximum ecosystem familiarity

### When TIP-20 is the better fit

Use TIP-20 when you are building on Tempo and need:

- stablecoin issuance
- payment references and reconciliation
- fee payment in stablecoins
- predictable payment throughput
- built-in compliance hooks
- issuer operational controls
- payment-native DEX routing
- native rewards distribution

---

## Practical Meaning for Issuers

For an issuer, the difference is largely about **how much payment logic is built into the standard**.

With ERC-20, you typically assemble a token stack yourself:

- token contract
- access control
- pause module
- compliance logic
- reward logic
- off-chain reconciliation conventions

With TIP-20, many of those concerns are brought into a more standardized framework:

- issuer controls
- policy integration
- memo support
- reward distribution
- Tempo-native payment and DEX integration

That can reduce implementation variance and make integrations more predictable.

---

## Backward Compatibility

Tempo explicitly describes TIP-20 as **building on ERC-20** and being **fully backward compatible**.

That means the familiar ERC-20 interaction model still exists for common wallet and dApp flows:

- balance lookup
- transfer
- approvals
- delegated transfers

But TIP-20 adds new standardized capabilities that payment-centric applications can rely on.

So the right mental model is:

> **TIP-20 is not a replacement for ERC-20 concepts.**
>
> **It is a payment-specialized superset for Tempo.**

---

## The Most Important Differences in One List

If you only remember a few points, remember these:

1. **ERC-20 is general-purpose; TIP-20 is payment-focused.**
2. **TIP-20 keeps ERC-20-style core functions but adds payment and issuer controls.**
3. **TIP-20 has native memo support; ERC-20 does not.**
4. **TIP-20 integrates with compliance policies; ERC-20 does not standardize that.**
5. **TIP-20 includes native rewards distribution; ERC-20 usually needs separate contracts.**
6. **TIP-20 is integrated with Tempo's fee model, payment lanes, and DEX logic.**
7. **TIP-20 standardizes six decimals; ERC-20 leaves decimals optional.**
8. **TIP-20 is implemented through Tempo's optimized protocol-native model rather than only issuer-defined contract logic.**

---

## Bottom Line

**ERC-20** is the foundational fungible token interface for Ethereum.

**TIP-20** takes that familiar base and adapts it for **stablecoins, payments, compliance, and issuer operations on Tempo**.

So the cleanest summary is:

> **ERC-20 defines how fungible tokens behave.**
>
> **TIP-20 defines how payment-oriented fungible tokens behave on Tempo.**

---

## References

- [Tempo Docs — TIP-20 Token Standard Overview](https://docs.tempo.xyz/protocol/tip20/overview)
- [Tempo Docs — TIP-20 Specification](https://docs.tempo.xyz/protocol/tip20/spec)
- [Tempo Docs — TIP-20 Rewards Overview](https://docs.tempo.xyz/protocol/tip20-rewards/overview)
- [Tempo Blog — TIP-20: a token standard for payments](https://tempo.xyz/blog/tip20)
- [Ethereum EIP-20 — Token Standard](https://eips.ethereum.org/EIPS/eip-20)
