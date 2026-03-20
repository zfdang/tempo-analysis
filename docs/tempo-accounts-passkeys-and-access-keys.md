# Tempo Accounts, Passkeys, and Access Keys

## Overview

Tempo's account layer is best understood as a combination of:

- familiar EVM wallet connectivity
- protocol-native support for modern signature schemes
- passkey-oriented onboarding
- scoped delegated keys for repeat or automated actions

This means Tempo does not force developers into only one account model.

Instead, it offers two main account experiences:

1. **embedded, domain-bound passkey accounts**
2. **universal EVM wallet connections**

And underneath both experiences, Tempo's transaction layer adds capabilities that ordinary Ethereum EOAs do not have natively.

## 1. Two Ways to Enter the Account Layer

### 1.1 Domain-bound passkey accounts

Tempo supports embedded accounts built around **WebAuthn passkeys**.

In this model:

- the user creates or uses a passkey on your application domain
- the credential is bound to that domain as a WebAuthn relying party
- the user authenticates with platform biometrics such as Face ID, Touch ID, or fingerprint unlock
- the private key material stays in the device's secure enclave or platform credential store

This is a strong onboarding path for applications that want a native, passwordless, app-embedded account experience.

The tradeoff is portability:

- a passkey created for one domain does not automatically work on another application's domain

So this is an **embedded account** model, not a universal wallet model.

### 1.2 Connected EVM wallets

Tempo also supports the familiar wallet path:

- MetaMask-style injected wallets
- Wagmi wallet connectors
- custom-network wallet setup

This is the better fit when an application wants a **universal account experience** that can move across apps.

Tempo's docs explicitly frame the choice this way:

- use passkeys for a domain-bound embedded account experience
- use wallets for a universal account experience

Applications can also offer both.

## 2. What Makes a Tempo Account Different

Tempo's special account behavior does not come from inventing an entirely separate account object onchain.

It comes from the fact that the transaction layer supports multiple signature and authorization patterns directly.

In practice, Tempo accounts can be controlled through:

- `secp256k1`
- `P256`
- `WebAuthn`
- `Keychain` signatures for authorized access keys

This matters because it lets Tempo support passkeys and scoped delegated keys without forcing every application to build a full smart-account stack first.

## 3. Root Keys and Access Keys

Tempo's account model has a useful hierarchy:

- a **root key** controls the account at the highest authority level
- one or more **access keys** can be authorized beneath it

For embedded passkey accounts, the root key is often a WebAuthn credential. For connected wallets, the root key is more likely a conventional wallet-controlled key.

## 4. What Access Keys Are For

Passkeys are great for secure onboarding, but they can be clumsy if the user must approve every single action with a biometric prompt.

That is the main reason Tempo includes **Access Keys**.

Access Keys let a root key authorize a secondary key that can sign on behalf of the account with restrictions such as:

- expiry time
- per-token spending limits
- reduced privileges

This is one of Tempo's most important account-layer ideas because it bridges:

- strong end-user authentication
- smoother repeated interactions
- safer delegated automation

## 5. The Account Keychain Precompile

Tempo's access-key system is enforced by the **Account Keychain precompile** at:

`0xAAAAAAAA00000000000000000000000000000000`

The precompile manages authorized keys for each account and stores metadata such as:

- signature type
- expiry timestamp
- whether spending limits are enforced
- revocation state

It also tracks remaining per-token spending limits for keys that have them.

## 6. What Access Keys Can and Cannot Do

The specification describes a strict hierarchy.

### Root key

The root key:

- has full authority over the account
- can authorize and revoke access keys
- can update spending limits
- is not subject to access-key spending limits

### Access key

An access key:

- can sign transactions on behalf of the account
- may have an expiry timestamp
- may have per-TIP-20 spending limits
- cannot authorize new keys
- cannot modify its own permissions through mutable precompile calls

This is what makes access keys useful for delegation without making them equivalent to the root account credential.

## 7. Spending Limits in More Detail

Tempo's access-key limits are token-specific.

The Account Keychain specification states that these limits apply to direct account calls involving certain TIP-20 methods, including:

- `transfer()`
- `transferWithMemo()`
- `approve()`
- `startReward()`

The limits are designed to constrain direct account spending behavior rather than every possible downstream contract effect in the whole EVM.

That is an important nuance:

- access keys are a practical delegation tool
- they are not a universal formal policy engine for all possible contract behavior

## 8. Key Managers and Passkey Infrastructure

Passkey accounts need more than onchain validation. Applications also need a way to manage the public-key side of WebAuthn credentials.

Tempo's TypeScript tooling exposes this through a **Key Manager** concept.

The docs show two broad patterns:

- local development or demo storage
- remote server-backed key management

Tempo explicitly warns that local browser storage is not a production-safe long-term choice for key management, because users can lose local state or move across devices.

That is why remote key-manager infrastructure matters in real deployments.

This is a good example of Tempo's account layer spanning both:

- protocol-native primitives
- application-side operational infrastructure

## 9. How Passkeys, Access Keys, and `0x76` Fit Together

These features are easiest to understand when separated into layers.

### Transaction layer

Tempo's `0x76` transaction type provides:

- alternative signature schemes
- fee sponsorship
- batching
- timing windows
- parallelizable nonces
- access-key authorization hooks

### Account layer

The account layer builds on that with:

- passkey-based root credentials
- access-key delegation
- connected-wallet compatibility

### Application layer

Applications then use those capabilities to build:

- embedded sign-up flows
- limited-power session or automation keys
- smoother payment UX
- machine-payment integrations

So the account model is not independent from `0x76`. It is one of the main reasons `0x76` exists.

## 10. Why Tempo Designed Accounts This Way

Tempo is trying to solve two problems at once.

### 10.1 Make onboarding easier

Passkeys reduce friction for:

- non-crypto-native users
- embedded wallet experiences
- mobile-first apps

### 10.2 Make repeated actions safer and smoother

Access keys reduce the cost of repeated approval prompts while still preserving bounded authority.

That matters for:

- highly interactive apps
- merchant or consumer payment flows
- agentic software
- MPP sessions
- delegated service calls

## 11. Tempo's Account Model vs. Plain Ethereum Thinking

Ethereum developers often think in terms of a simple split:

- EOA
- smart contract wallet

Tempo fits awkwardly into that exact frame.

It is closer to an account-abstraction-style experience, but much of the useful behavior is made protocol-native instead of being pushed entirely into user-deployed account contracts.

That is why Tempo account UX can feel more advanced than a plain EOA model even when the external developer experience still looks wallet-like.

## 12. A Practical Mental Model

If you are deciding how to explain Tempo accounts to a reader or a product team, this is a good shorthand:

- **Passkey account**: best for embedded, domain-bound onboarding
- **Connected wallet**: best for universal portability across apps
- **Access key**: best for bounded repeated actions after initial trust is established

And underneath all three:

- Tempo Transactions provide the signature and authorization machinery
- the Account Keychain enforces delegated-key restrictions

## 13. Typical Flow

One common Tempo account flow looks like this:

1. A user signs up with a passkey on an application's domain.
2. The application stores or resolves the credential's public-key material through a key manager.
3. The passkey acts as the account's root credential for initial high-trust actions.
4. The account authorizes an access key with expiry or TIP-20 spending limits.
5. That access key handles repeated low-risk actions, such as routine payments or service interactions, until expiry or revocation.

This flow helps explain why Tempo's account layer is important to the broader payments and agent-commerce story.

## References

- `https://docs.tempo.xyz/guide/use-accounts`
- `https://docs.tempo.xyz/guide/use-accounts/embed-passkeys`
- `https://docs.tempo.xyz/guide/use-accounts/connect-to-wallets`
- `https://docs.tempo.xyz/protocol/transactions/AccountKeychain`
- `https://docs.tempo.xyz/protocol/transactions/spec-tempo-transaction`
- `https://docs.tempo.xyz/quickstart/evm-compatibility`
- `https://docs.tempo.xyz/sdk/typescript/server/handler.keyManager`
