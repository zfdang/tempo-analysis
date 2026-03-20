# TIP-403 on Tempo: A Detailed Guide

## Overview

**TIP-403** is Tempo's **policy registry standard** for TIP-20 tokens.

Its purpose is to provide a **shared, reusable compliance and access-control layer** that TIP-20 tokens can reference when deciding whether a transfer should be allowed.

Instead of forcing every token issuer to implement its own whitelist or blacklist logic, TIP-403 centralizes policy management in a registry. A TIP-20 token can store a `transferPolicyId`, and during transfers it checks the TIP-403 registry to determine whether the sender and recipient are authorized.

A concise mental model is:

> **TIP-20 defines the payment asset.**
>
> **TIP-403 defines who is allowed to move it.**

---

## Why TIP-403 Exists

Tempo is explicitly designed for payment systems, stablecoins, and regulated value transfer. In that environment, token issuers often need rules such as:

- KYC / AML gating
- jurisdiction-based transfer controls
- denylisting sanctioned or restricted addresses
- allowlisting verified users
- consistent controls across multiple related tokens

Without a standard policy layer, every token project would have to build its own custom logic. That creates several problems:

- duplicated engineering effort
- inconsistent enforcement across tokens
- harder audits and operations
- fragmented issuer tooling
- more difficult policy changes over time

TIP-403 solves this by moving transfer-policy logic into a **central registry** that can be shared across multiple TIP-20 tokens.

---

## The Core Idea

TIP-403 is a registry contract that stores policies identified by a unique `policyId`.

Each policy has:

- a **policy type**
- an **admin**
- a set of addresses associated with that policy

A TIP-20 token stores the `policyId` it wants to use. During transfers, the token checks the registry to determine whether both the sender and the recipient are authorized.

That means TIP-403 is not itself a token standard. It is a **policy-control layer** used by TIP-20 tokens.

---

## What TIP-403 Controls

At a high level, TIP-403 controls **transfer authorization**.

It does not define:

- token balances
- minting logic
- fee payment
- DEX behavior
- rewards accounting

Those are handled elsewhere in Tempo, primarily by TIP-20 and other protocol modules.

TIP-403 focuses narrowly on one question:

> **Should this address be allowed to participate in this token transfer?**

That narrow scope is part of its strength.

---

## Built-in Design Goals

TIP-403 is designed to provide:

- **shared compliance policies** across multiple tokens
- **simple and predictable authorization logic**
- **low implementation overhead** for token issuers
- **standardized operational controls**
- **interoperability** with other Tempo-native modules, especially TIP-20 and TIP-20 Rewards

This makes TIP-403 less like an application-specific compliance add-on and more like a protocol-native **policy control plane**.

---

## Registry Address

Tempo's documentation specifies that the TIP-403 registry is deployed at:

`0x403c000000000000000000000000000000000000`

That gives TIP-20 tokens and other integrations a standard onchain location for policy checks.

---

## Policy Types

TIP-403 supports exactly **two policy types**:

### 1. Whitelist policies

A whitelist policy means:

- addresses **in** the policy set are allowed
- addresses **not in** the policy set are blocked

This is useful when transfers should be restricted to approved participants only, such as:

- verified customers
- approved institutions
- licensed counterparties
- internal treasury accounts

### 2. Blacklist policies

A blacklist policy means:

- addresses **in** the policy set are blocked
- addresses **not in** the policy set are allowed

This is useful when transfers are generally open, but some addresses need to be excluded, such as:

- sanctioned addresses
- fraud-linked accounts
- compromised wallets
- accounts under operational restriction

This two-mode system is simple, but sufficient for many payment and stablecoin compliance patterns.

---

## Built-in Policies

TIP-403 reserves the first two policy IDs for built-in behavior:

- **`policyId = 0`** → **always-reject**
- **`policyId = 1`** → **always-allow**

This is a subtle but important design choice.

It means Tempo has two universal baseline policies available without requiring custom policy creation:

### `policyId = 0`: always-reject

This policy rejects all token transfers.

Possible uses include:

- freezing a token by policy
- safe default during initialization
- emergency fallback
- testing and restrictive deployment workflows

### `policyId = 1`: always-allow

This policy allows all token transfers.

Tempo documentation states that new TIP-20 tokens start with `transferPolicyId = 1`, meaning they default to open transfers unless the token admin changes the policy.

### Custom policy IDs start at 2

The registry's `policyIdCounter` starts at `2`, so every custom policy created by users or issuers receives an ID starting from that point.

---

## Storage Model

The TIP-403 registry maintains three core pieces of state:

### 1. `policyIdCounter`

This stores the next policy ID that will be assigned when a new custom policy is created.

### 2. `policyData`

This maps `policyId` to a `PolicyData` struct containing:

- the `policyType`
- the policy `admin`

### 3. `policySet`

This is the actual address membership set for each policy. Internally, it maps:

- policy ID
- address
- boolean membership state

This simple storage model helps keep authorization checks easy to reason about.

---

## Policy Lifecycle

A TIP-403 policy usually follows this lifecycle:

### Step 1: Create a policy

A policy is created using either:

- `createPolicy(...)`
- `createPolicyWithAccounts(...)`

The caller chooses:

- the admin address
- the policy type
- optionally, an initial set of accounts

Anyone can create a policy, but the creator specifies which address will control that policy going forward.

### Step 2: Populate the policy set

The policy admin then adds or removes addresses.

For whitelist policies, adding an address means **authorizing** it.

For blacklist policies, adding an address means **restricting** it.

### Step 3: Attach the policy to a TIP-20 token

A TIP-20 token stores a `transferPolicyId`. The token admin can change that ID through the token's own administrative flow.

Once attached, future transfers are checked against the chosen TIP-403 policy.

### Step 4: Update the policy over time

The policy admin can keep modifying the underlying set of addresses without redeploying the token or replacing the token contract itself.

This is one of the biggest operational advantages of TIP-403.

---

## Main Interface

The TIP-403 interface in the Tempo docs includes the following major functions.

---

## Policy creation

### `createPolicy(address admin, PolicyType policyType)`

Creates a new empty policy.

Use this when you want to create the policy first and populate it afterward.

### `createPolicyWithAccounts(address admin, PolicyType policyType, address[] calldata accounts)`

Creates a new policy and immediately seeds it with addresses.

Use this when you already know the initial participants and want a single-step setup flow.

---

## Policy administration

### `setPolicyAdmin(uint64 policyId, address admin)`

Transfers policy admin rights to another address.

This is important for operational delegation and governance changes.

### `modifyPolicyWhitelist(uint64 policyId, address account, bool allowed)`

Adds or removes an address from a whitelist policy.

- `allowed = true` means add the address to the whitelist
- `allowed = false` means remove the address from the whitelist

This function reverts if the specified policy is not a whitelist.

### `modifyPolicyBlacklist(uint64 policyId, address account, bool restricted)`

Adds or removes an address from a blacklist policy.

- `restricted = true` means add the address to the blacklist
- `restricted = false` means remove the address from the blacklist

This function reverts if the specified policy is not a blacklist.

---

## Policy queries

### `isAuthorized(uint64 policyId, address user)`

Returns whether an address is authorized under the specified policy.

This is the core query function used during token transfer checks.

### `policyIdCounter()`

Returns the next policy ID that will be assigned to a newly created policy.

### `policyExists(uint64 policyId)`

Returns whether the policy exists.

The built-in policy IDs `0` and `1` always exist.

---

## Authorization Logic

TIP-403 authorization is intentionally simple.

The docs describe the logic as:

- if `policyId == 0`, authorization returns `false`
- if `policyId == 1`, authorization returns `true`
- if the policy is a whitelist, authorization returns whether the address is in the set
- if the policy is a blacklist, authorization returns the inverse of set membership

This is important because it makes policy behavior easy to audit and easy to reason about.

In pseudocode:

```text
if policyId == 0:
    return false

if policyId == 1:
    return true

if policyType == WHITELIST:
    return address in policySet
else:
    return address not in policySet
```

---

## Admin Model

Each policy has a single `admin` stored in `PolicyData`.

That admin can:

- change the policy admin
- add or remove addresses in the policy set

The admin model is intentionally simple and direct.

It does not try to prescribe governance, multisig structures, or role hierarchies inside TIP-403 itself. Those can be layered on externally by choosing an admin address that is:

- an EOA
- a multisig
- a governance contract
- a treasury account
- an operational control account

This makes TIP-403 flexible without making the registry itself too complex.

---

## Events

The spec defines events so integrations can monitor policy changes onchain.

Important events include:

- `PolicyCreated`
- `PolicyAdminUpdated`
- `WhitelistUpdated`
- `BlacklistUpdated`

Operationally, these events are useful for:

- compliance monitoring
- indexers
- issuer dashboards
- audit trails
- offchain synchronization tools

---

## Errors

The spec also defines clear error conditions, including:

- `Unauthorized()` when a caller is not the policy admin
- `IncompatiblePolicyType()` when a caller tries to use a whitelist function on a blacklist policy, or vice versa

This improves safety and clarity for contract integrations and tooling.

---

## How TIP-403 Works with TIP-20

This is the most important relationship in the system.

TIP-20 tokens store the current TIP-403 `transferPolicyId` in token storage.

During token transfers, the TIP-20 token checks the registry by calling `isAuthorized()` for:

- the **sender**
- the **recipient**

This is a very important detail.

It means TIP-403 is not only a "sender restriction" model. It can also prevent transfers **to** unauthorized addresses.

That design is useful for regulated payment systems because it can enforce both:

- who is allowed to send
- who is allowed to receive

Tempo's docs also state:

- new TIP-20 tokens start with `transferPolicyId = 1` (`always-allow`)
- when a token's transfer policy is changed, future transfers immediately use the new policy

So TIP-403 gives TIP-20 tokens a live, changeable compliance layer without requiring token redeployment.

---

## Why Shared Policies Matter

One of TIP-403's strongest features is that policies can be reused across multiple tokens.

That means an issuer operating multiple stablecoins or payment instruments can keep transfer rules consistent without duplicating policy logic in every token.

Examples:

- one whitelist policy reused across multiple regulated USD-denominated tokens
- one blacklist policy reused across a family of payment products
- one internal treasury-only whitelist reused across settlement tokens
- one shared restricted-address list used across both payment and rewards tokens

This makes compliance administration much cleaner.

Instead of asking, "Did we update all token contracts correctly?", an operator can ask, "Did we update the shared policy registry entry correctly?"

---

## TIP-403 and TIP-20 Rewards

TIP-20 Rewards documentation explicitly states that reward transfers remain compliant with TIP-403 transfer policies.

This matters because it means policy enforcement is not isolated to ordinary transfers. It also influences reward distribution behavior.

In practice, that helps ensure that:

- restricted addresses do not bypass controls through rewards
- token incentives stay aligned with token compliance rules
- wallet UX is simpler because the same policy framework applies across multiple token operations

So TIP-403 is not only relevant to transfers in the narrow sense. It also affects how adjacent token functionality remains policy-compliant.

---

## Strengths of TIP-403

### 1. Standardization

It gives Tempo a shared way to express token transfer policies rather than leaving every issuer to invent custom patterns.

### 2. Reusability

Policies can be shared across multiple TIP-20 tokens.

### 3. Operational flexibility

Issuers can update policy membership over time without redeploying tokens.

### 4. Simplicity

Only two policy types, simple admin model, clear authorization logic.

### 5. Ecosystem consistency

Because TIP-20 and TIP-20 Rewards already integrate with TIP-403, the policy layer can remain consistent across multiple Tempo-native modules.

---

## Practical Limitations

TIP-403 is intentionally simple, and that means it does **not** try to solve every compliance use case by itself.

For example, TIP-403 does not natively encode:

- time-based rules
- transfer size limits
- jurisdiction matrices
- velocity controls
- transaction purpose codes
- conditional policy logic based on external data

Those kinds of policies would require higher-level systems, custom workflows, or future extensions.

So TIP-403 is best understood as a **foundational compliance primitive**, not a complete compliance operating system.

---

## Example Use Cases

### Regulated stablecoin issuance

An issuer creates a whitelist policy and only approved customers are allowed to send and receive the stablecoin.

### Open token with denylist controls

An issuer uses a blacklist policy so transfers remain generally open, but sanctioned or fraudulent addresses can be blocked.

### Shared policy across multiple products

A payments company issues several TIP-20 tokens but wants one unified compliance set across all of them.

### Treasury-only settlement token

An internal settlement token uses a whitelist policy so only designated treasury and settlement accounts can participate.

---

## A Simple Example Flow

Here is the conceptual setup flow:

1. Create a TIP-403 policy
2. Choose whitelist or blacklist mode
3. Set the policy admin
4. Add initial addresses
5. Set the token's `transferPolicyId`
6. Let the TIP-20 token enforce sender and recipient checks automatically
7. Update the policy set over time as business requirements change

In simplified form:

```text
issuer creates policy
    ↓
issuer adds approved or restricted addresses
    ↓
token admin points token to policyId
    ↓
every transfer checks sender and recipient
    ↓
admin updates policy membership as needed
```

---

## The Best Mental Model

If you are trying to remember TIP-403 in one sentence, use this:

> **TIP-403 is Tempo's shared transfer-authorization registry for TIP-20 tokens.**

And if you want the slightly longer version:

> **TIP-403 gives Tempo a reusable whitelist/blacklist policy layer so TIP-20 tokens can enforce compliance and access-control rules without embedding custom policy logic in every token.**

---

## Bottom Line

TIP-403 is one of the key pieces that makes Tempo's payment stack feel operationally serious.

By separating **asset behavior** from **transfer authorization**, Tempo allows:

- more reusable token infrastructure
- cleaner issuer operations
- consistent enforcement across token families
- easier policy updates over time

In practical terms:

- **TIP-20** says what the token is
- **TIP-403** says who is allowed to move it

That separation is simple, but powerful.

---

## References

- [Tempo Docs — TIP-403 Specification](https://docs.tempo.xyz/protocol/tip403/spec)
- [Tempo Docs — TIP-20 Overview](https://docs.tempo.xyz/protocol/tip20/overview)
- [Tempo Docs — TIP-20 Rewards Overview](https://docs.tempo.xyz/protocol/tip20-rewards/overview)
