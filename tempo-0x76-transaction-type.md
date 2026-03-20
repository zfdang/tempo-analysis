# Tempo `0x76` Transaction Type

This document is a technical summary of Tempo's `0x76` transaction type based on the official Tempo documentation and the EIP-2718 typed transaction model.

## Overview

Tempo defines a custom typed transaction with type byte `0x76`. It is a Tempo-specific extension built on top of [EIP-2718](https://eips.ethereum.org/EIPS/eip-2718), which standardizes the envelope format:

```text
TransactionType || TransactionPayload
```

Under EIP-2718, the first byte identifies the transaction format, and the remaining bytes are interpreted according to that format. Tempo uses this mechanism to introduce a richer transaction model while preserving a familiar typed-transaction dispatch model for clients and tooling.

In practice, the `0x76` transaction type turns several higher-level wallet and payment features into protocol-native behavior rather than pushing them into external account contracts, paymaster systems, or bundler infrastructure.

## Relationship to EIP-2718

EIP-2718 does not define the semantics of a specific transaction type by itself. It defines a namespace and envelope for future transaction types. Tempo's `0x76` transaction is one such chain-specific typed transaction.

Key points:

- `0x76` is the Tempo transaction type byte.
- It fits the EIP-2718 typed transaction model.
- The payload is RLP-encoded.
- The transaction is only meaningful on Tempo; it is not a standard Ethereum mainnet transaction type.

So the relationship is:

- EIP-2718 provides the container format.
- Tempo defines the payload schema, signing rules, validation logic, and execution semantics for type `0x76`.

## Why Tempo Introduced `0x76`

Tempo uses `0x76` to solve several limitations of ordinary Ethereum-style EOAs and standard typed transactions:

- Native support for passkey-friendly signature schemes
- Parallelizable nonces instead of a single strictly sequential nonce stream
- Fee sponsorship without paymasters or bundlers
- Multi-call batching without wrapper contracts
- Time-windowed execution for scheduled or expiring transactions
- Scoped access keys with optional expiry and spending limits
- EIP-7702-style authorization lists extended to Tempo's account abstraction model

In other words, `0x76` is not just "another transaction type." It is the protocol surface that Tempo uses for modern account, payment, and wallet behavior.

## High-Level Structure

At a high level, the signed transaction envelope is:

```text
0x76 || rlp([
  chain_id,
  max_priority_fee_per_gas,
  max_fee_per_gas,
  gas_limit,
  calls,
  access_list,
  nonce_key,
  nonce,
  valid_before,
  valid_after,
  fee_token,
  fee_payer_signature,
  aa_authorization_list,
  key_authorization?, 
  sender_signature
])
```

Important fields:

- `chain_id`, `max_priority_fee_per_gas`, `max_fee_per_gas`, `gas_limit`: familiar fee and replay-protection fields in the EIP-1559 style
- `calls`: a list of calls executed atomically in one transaction
- `access_list`: EIP-2930-style access list support
- `nonce_key` and `nonce`: Tempo's 2D nonce model
- `valid_before` and `valid_after`: optional execution time window
- `fee_token`: optional fee token preference
- `fee_payer_signature`: optional sponsorship signature
- `aa_authorization_list`: EIP-7702-style authorization list
- `key_authorization`: optional access-key provisioning payload
- `sender_signature`: the actual sender-side Tempo signature

Tempo also defines a `Call` item as:

```text
rlp([to, value, input])
```

The `calls` list must contain at least one call, and the entire list executes atomically.

## What `0x76` Adds Beyond Standard Ethereum Transactions

### 1. Native Multi-Call Batching

Instead of carrying a single call target plus calldata, a Tempo transaction carries a `calls` array. This lets one transaction execute multiple operations atomically.

That matters for:

- Payment flows that need approve-and-execute behavior
- Wallet UX that would otherwise require multiple sequential transactions
- Contract interactions that benefit from protocol-level atomic batching

This is conceptually similar to using a multicall contract, but the batching primitive is built directly into the transaction type.

### 2. Alternative Signature Schemes

Tempo's `0x76` transaction supports multiple signature types natively:

- `secp256k1`
- `P256`
- `WebAuthn`
- `Keychain` signatures for access-key flows

This is one of the most important differences from ordinary Ethereum EOAs. It means Tempo can support passkey-oriented account UX at the protocol transaction level instead of requiring a smart-account wrapper just to validate non-`secp256k1` signatures.

The spec identifies signatures by length and wire prefix:

- `secp256k1`: 65 bytes, no type prefix
- `P256`: prefix `0x01`
- `WebAuthn`: prefix `0x02`
- `Keychain`: prefix `0x03`

`WebAuthn` support is especially important because it gives Tempo a direct path to passkey-based authentication.

### 3. Fee Sponsorship

Tempo bakes gas sponsorship directly into the transaction type through `fee_payer_signature`.

This allows:

- the sender to authorize the transaction itself
- a third-party sponsor to separately authorize paying the fees

The design uses dual signing domains:

- sender domain: transaction type byte `0x76`
- fee payer domain: magic byte `0x78`

This domain separation prevents signature reuse between the sender role and the sponsor role.

At the moment, the fee payer path is specified as `secp256k1`-only.

An important detail from the spec is that when a fee payer is present, the sender signs a version of the transaction where the fee-token slot is left empty and the fee-payer slot uses a placeholder. The fee payer then signs a separate sponsor-oriented hash that commits to the sender and the fee token. This gives the sponsor flexibility while still making the sponsor's commitment explicit.

The result is a protocol-native gas sponsorship model that does not require an ERC-4337 paymaster or bundler.

### 4. Configurable Fee Tokens

Tempo positions `0x76` as the preferred transaction type for payment-centric applications because it can integrate directly with Tempo's fee-token model.

According to the official guide, Tempo Transactions support paying transaction fees with supported USD-denominated TIP-20 stablecoins through Tempo's fee system and Fee AMM. That makes the transaction type better aligned with stablecoin payment applications than standard Ethereum transactions, which normally assume payment in the chain's native gas asset.

### 5. Parallelizable 2D Nonces

Standard Ethereum transactions use a single strictly increasing nonce per account. Tempo extends this with:

- `nonce_key`
- `nonce`

This creates a two-dimensional nonce space:

- nonce key `0` is the protocol nonce
- nonce keys `1..N` are user nonce lanes

The practical effect is that one account can maintain multiple independent nonce streams and submit transactions concurrently without forcing everything through one global sequence.

This is a major throughput and UX improvement for:

- apps sending many user transactions quickly
- agents or services issuing multiple actions in parallel
- wallets that want to avoid nonce contention

### 6. Scheduled and Time-Bounded Execution

The fields `valid_after` and `valid_before` allow Tempo transactions to express a validity window.

This enables:

- scheduled execution
- expiring transactions
- automation flows where the transaction should only be accepted within a defined time range

This capability is native to the transaction format rather than being implemented in application-specific contract logic.

### 7. Access Keys

Tempo's `key_authorization` field allows a root account to provision a scoped access key.

The access-key model supports:

- multiple key types
- optional expiry timestamps
- optional TIP-20 spending limits
- protocol-native enforcement through the Account Keychain precompile

This matters because it lets a high-trust root credential, such as a passkey, delegate limited authority to a secondary key for repeated or automated actions without prompting the root signer every time.

Tempo also defines a `Keychain` signature format so an authorized access key can sign on behalf of the root account in a verifiable way.

### 8. EIP-7702-Style Authorization Lists

Tempo includes `aa_authorization_list`, which follows EIP-7702-style delegation semantics but extends them to Tempo's broader signature model.

Compared with baseline EIP-7702 behavior, Tempo adds support for:

- `secp256k1`
- `P256`
- `WebAuthn`

This means passkey-based or P256-based accounts can participate in 7702-style delegation flows on Tempo.

## Signature and Validation Model

The `0x76` transaction type is designed around protocol-native validation rather than external account logic.

At a high level, validation includes:

- determining the sender signature type
- validating the sender signature
- validating the selected nonce lane
- optionally validating a fee payer signature
- optionally validating access-key authorization
- optionally validating EIP-7702-style authorizations

For access-key flows, Tempo uses the Account Keychain precompile at:

```text
0xAAAAAAAA00000000000000000000000000000000
```

This precompile manages authorized access keys, expiry, and spending limits.

## Why `0x76` Is More Than an EVM Convenience Feature

Tempo's `0x76` transaction type effectively brings together three different design directions under one typed envelope:

- account abstraction features
- payment-specific UX features
- wallet-native usability features

From a systems perspective, it lets Tempo do at the transaction layer what Ethereum often handles through a mix of:

- smart-account contracts
- paymasters
- bundlers
- multicall contracts
- application-specific scheduling logic

Compared with Ethereum's common patterns:

- EIP-4337 goals such as sponsorship, batching, and alternative signatures are pushed into the protocol
- EIP-7702 delegation is supported, but Tempo adds extra signature schemes and native features around it

## Practical Implications for Builders

If you are building on Tempo, `0x76` is the transaction type to understand first because it is the transaction model that exposes Tempo's distinctive capabilities.

It is especially relevant when your application needs any of the following:

- passkey accounts
- sponsored transactions
- stablecoin-centric fee payment
- batched execution
- high-throughput concurrent transaction submission
- scoped session-like keys or delegated signer permissions
- scheduled payment or automation flows

## Summary

Tempo's `0x76` transaction type is a Tempo-specific EIP-2718 typed transaction that packages modern wallet and payment features into the protocol itself.

At the format level, it is "just" a typed transaction envelope with an RLP payload. At the semantic level, it is much more than that: it is the core transaction primitive Tempo uses for passkeys, gas sponsorship, batching, 2D nonces, access keys, scheduled execution, configurable fee tokens, and extended EIP-7702-style delegation.

That is the key idea to keep in mind:

- EIP-2718 provides the envelope.
- Tempo `0x76` defines the payment- and account-oriented transaction semantics inside that envelope.

## References

- [Tempo Transaction specification](https://docs.tempo.xyz/protocol/transactions/spec-tempo-transaction)
- [Use Tempo Transactions](https://docs.tempo.xyz/guide/tempo-transaction)
- [EIP-4337 and Tempo Transactions](https://docs.tempo.xyz/protocol/transactions/eip-4337)
- [EIP-7702 and Tempo Transactions](https://docs.tempo.xyz/protocol/transactions/eip-7702)
- [EIP-2718: Typed Transaction Envelope](https://eips.ethereum.org/EIPS/eip-2718)
