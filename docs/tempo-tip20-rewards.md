# TIP-20 Rewards Distribution

## Overview

**TIP-20 Rewards** is a built-in, opt-in reward distribution mechanism that allows issuers to distribute rewards to token holders proportionally based on their holdings, without requiring a separate staking contract.

This is an important part of the Tempo stack because it turns reward distribution into a **protocol-native feature** rather than forcing every issuer to build a separate staking or yield mechanism.

A concise mental model is:

> **TIP-20 defines the payment asset.**
>
> **TIP-20 Rewards distributes value to holders of that asset.**

---

## Why TIP-20 Rewards Exists

Many payment token and stablecoin use cases require pro-rata distribution of value to holders:

- interest-bearing stablecoins
- yield distribution from treasury operations
- incentive programs
- deterministic inflation mechanisms
- staking-like rewards without requiring separate staking contracts

On most EVM chains, this requires deploying a separate staking or rewards contract. Users must transfer tokens into that contract, which fragments holdings and complicates wallet UX.

TIP-20 Rewards solves this by integrating the distribution mechanism directly into the token standard. Users opt in without moving their tokens, and rewards accrue automatically in proportion to their holdings.

---

## How It Works

### The Accumulator Pattern

TIP-20 Rewards uses a **reward-per-token accumulator pattern** that scales efficiently regardless of the number of holders.

The core mechanism:

- A `globalRewardPerToken` value tracks the cumulative rewards distributed per token, scaled by 1e18
- Each opted-in user stores a `rewardPerToken` snapshot at the time of their last interaction
- Pending rewards for a user are calculated as: `(globalRewardPerToken - user_snapshot) * user_balance`

When rewards are distributed, the update is:

```text
deltaRPT = amount * 1e18 / optedInSupply
globalRewardPerToken += deltaRPT
```

This means distribution is **constant-time**: one update to a global accumulator, regardless of how many holders are opted in.

### Opt-In Model

Users must explicitly opt in by calling `setRewardRecipient(recipient)`:

- setting a non-zero `recipient` address opts in
- setting `recipient` to `address(0)` opts out
- when opted in, the user's balance contributes to `optedInSupply`
- rewards can be delegated to a different address than the holder

This opt-in model is important because:

- it respects holder preferences
- it avoids forcing compliance-sensitive accounts into reward flows
- it lets users delegate reward claims to a separate address

### Claiming Rewards

Opted-in users (or their designated recipients) can call `claimRewards()` to receive accrued rewards. Rewards accrue automatically on balance-changing operations (transfers, mints, burns).

### Instant Distribution

The current specification supports **instant distributions** where rewards are added immediately to the accumulator. Time-based streaming distributions are planned for a future upgrade.

---

## Core Interface

The TIP-20 Rewards functions are part of the TIP-20 token interface:

### `distributeReward(uint256 amount)`

Distributes `amount` of tokens as rewards to all opted-in holders proportionally.

Anyone can call this function. The caller must have sufficient token balance, and the transfer must pass TIP-403 policy checks.

### `setRewardRecipient(address newRewardRecipient)`

Sets the reward recipient for the caller:

- non-zero address: opts in and designates where rewards are sent
- `address(0)`: opts out of rewards

### `claimRewards() → uint256 maxAmount`

Claims all pending rewards for the caller and returns the amount claimed.

### `userRewardInfo(address user) → (address, uint256, uint256)`

Returns the user's:

- `rewardRecipient` — where rewards are sent
- `rewardPerToken` — the user's snapshot of the global accumulator
- `rewardBalance` — unclaimed rewards

### State Queries

- `globalRewardPerToken()` — the current cumulative reward-per-token value
- `optedInSupply()` — the total token balance of all opted-in holders

---

## TIP-403 Integration

All reward-related token movements must comply with TIP-403 transfer policies:

- `distributeReward`: validates that the funder (caller) is authorized
- `setRewardRecipient`: validates both the holder and the recipient address
- `claimRewards`: validates the caller

This ensures that reward distribution does not bypass compliance controls. Restricted addresses cannot receive rewards through the reward mechanism if they would be blocked from receiving ordinary transfers.

This is an important design property: **the same policy framework applies across all token operations**, not just regular transfers.

---

## Invariants

The specification defines key invariants:

- `globalRewardPerToken` must monotonically increase (rewards cannot be withdrawn from the accumulator)
- `optedInSupply` must equal the sum of balances for all opted-in users
- all token movements must comply with TIP-403 policies

---

## Why This Matters for the Tempo Stack

### 1. Simpler wallet UX

Users do not need to "stake" tokens in a separate contract. They hold tokens in their wallet, opt in, and rewards accrue automatically. This is a much better experience than managing separate staking positions.

### 2. Better for stablecoin issuers

Interest-bearing stablecoins and yield-generating payment tokens can use this mechanism directly, without deploying and maintaining separate reward infrastructure.

### 3. Compliance-aware by default

Because TIP-403 policies apply to reward flows, issuers get consistent compliance enforcement across transfers, mints, burns, and rewards.

### 4. Efficient at scale

The accumulator pattern means the cost of distributing rewards is O(1), not O(n) where n is the number of holders. This matters for tokens with large holder populations.

---

## Use Cases

- **Interest-bearing stablecoins**: Distribute yield to opted-in holders without requiring them to deposit into a separate vault
- **Incentive programs**: Distribute bonus tokens proportionally to holders of a specific payment token
- **Treasury sharing**: Share protocol revenue with token holders
- **Loyalty programs**: Reward active stablecoin holders in payment ecosystems

---

## The Right Mental Model

A concise way to think about TIP-20 Rewards:

> **TIP-20 Rewards is a built-in, constant-time, opt-in reward distribution system that lets issuers distribute value to holders proportionally, without staking contracts, and with full TIP-403 compliance.**

---

## References

- TIP-20 Rewards Overview: https://docs.tempo.xyz/protocol/tip20-rewards/overview
- TIP-20 Rewards Specification: https://docs.tempo.xyz/protocol/tip20-rewards/spec
- Guide — Distribute Rewards: https://docs.tempo.xyz/guide/issuance/distribute-rewards
