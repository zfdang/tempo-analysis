# Tempo Fees and Fee AMM

## Overview

Tempo's fee system is one of the clearest places where the chain stops behaving like canonical Ethereum and starts behaving like a payments network.

On Ethereum, fees are normally paid in the chain's native token. On Tempo:

- there is no native gas token in normal user UX
- fees are denominated in USD terms
- users can pay fees in supported USD-denominated TIP-20 stablecoins
- validators can still prefer to receive fees in a different stablecoin
- the protocol bridges that mismatch through the **Fee AMM**

This document explains that fee layer, why Tempo designed it this way, and how it supports the rest of the stack.

## 1. Why This Layer Exists

Tempo is trying to make stablecoin payments feel native.

That goal creates a problem for a normal Ethereum-style fee model:

- merchants and users want to hold payment assets, not a separate volatile gas token
- wallets should not need to explain "you have USDC, but you cannot transact because you lack ETH"
- payment applications need predictable unit economics
- machine-payment flows need low-friction submission, sponsorship, and fee selection

Tempo's answer is to treat fees as a **stablecoin conversion and settlement problem**, not as a native-token problem.

## 2. How Tempo Differs from Ethereum

### 2.1 No Native Gas Token

Tempo does not expect users to hold a separate chain-native asset just to pay gas.

Instead:

- fees are priced in USD terms
- fee payment happens in supported TIP-20 stablecoins
- wallet UX centers on **fee-token selection**, not on native-token balance management

This is one of the biggest conceptual differences between Tempo and Ethereum.

### 2.2 Fixed Base Fee Instead of Ethereum's Dynamic Base Fee

Tempo does not use Ethereum's dynamic EIP-1559-style base fee adjustment.

Instead, the fee specification describes:

- a **fixed base fee**
- priority fees for inclusion preference
- payment lanes that protect payment throughput during congestion

The purpose is not to maximize fee-market expressiveness. It is to keep payment costs predictable.

### 2.3 Payment Lanes Support Fee Predictability

Tempo's network layer reserves most blockspace for payment transactions. That matters to the fee system because payment applications care about:

- stable inclusion
- stable price expectations
- resistance to unrelated congestion from non-payment workloads

So the fee model is not isolated from the blockspace model. The two are designed together.

## 3. Fee Units and Fee Calculation

Tempo specifies gas prices in **attodollars per gas**.

- `1 attodollar = 10^-18 USD`
- TIP-20 stablecoins use `6` decimal places, so `1 token unit = 1 microdollar = 10^-6 USD`

The fee spec describes the conversion from gas accounting into token units as:

```text
fee_in_microdollars = ceil(base_fee * gas_used / 10^12)
```

This extra precision matters because very low payment fees would be too coarse if the protocol tried to express everything directly in 6-decimal token units per gas.

## 4. Who Pays the Fee

By default, the sender pays the fee.

Tempo also supports **fee sponsorship**. In that case:

- the sender authorizes the transaction logic
- a separate `fee_payer` authorizes paying the fee
- the transaction is only valid if both signatures and the fee conditions are valid

This is tightly connected to Tempo's `0x76` transaction type. In practice, the fee layer and the transaction layer are separate topics, but they work together constantly.

## 5. How Fee Token Selection Works

Tempo does not always pick the fee token the same way. The fee specification defines an order of preference.

The protocol checks fee-token preference in this order:

1. the transaction's explicit `fee_token`
2. the fee payer's account-level default on the FeeManager
3. the TIP-20 token being called, for certain token methods
4. the DEX `tokenIn` for certain swap calls
5. `pathUSD` as the fallback

At the selected level, the chosen token must satisfy three conditions:

- it must be a USD-denominated TIP-20 token
- the fee payer must have enough balance
- there must be enough Fee AMM liquidity to convert it into the validator's preferred token

If any of those checks fail, the transaction is invalid.

## 6. The Fee Payment Lifecycle

At a high level, Tempo processes fees in three stages.

### 6.1 Before execution

Before transaction execution, the protocol:

- determines the `fee_payer`
- determines the `fee_token`
- computes the transaction's maximum fee exposure from gas limit and gas price
- deducts that maximum fee from the fee payer in the chosen token
- reserves enough Fee AMM liquidity to convert that token into the validator's preferred token

If liquidity is missing, the transaction is invalid before execution completes.

### 6.2 After execution

After execution, the protocol:

- computes the unused gas refund
- refunds the excess in the original fee token
- keeps the net fee amount as the actual fee paid

So the user-facing fee token remains stable from the payer's point of view, even though the validator may ultimately receive another token.

### 6.3 Validator settlement

Fees accumulate through the fee system and are claimable by validators in the token they prefer to receive.

That is the reason the conversion layer exists at all: user token and validator token do not need to match.

## 7. What the Fee AMM Does

The **Fee AMM** is a protocol-specific conversion layer for transaction fees.

It is not a general-purpose DEX for user trading. Its job is narrower:

- convert the payer's fee token into the validator's preferred token
- do so at fixed protocol-defined rates
- minimize MEV and fee-payment unpredictability

The Fee AMM specification describes **directional pools**:

- each pool is for `userToken -> validatorToken`
- fee swaps happen in that direction at a fixed rate
- rebalancing happens in the reverse direction at another fixed rate

### 7.1 Fixed-rate fee swaps

For protocol fee conversion, the Fee AMM uses a fixed fee-swap rate of:

```text
0.9970 validatorToken per 1.0 userToken
```

This is the conversion path used by the protocol during fee handling.

### 7.2 Rebalancing swaps

The system also allows public rebalancing in the opposite direction at a different fixed rate:

```text
1.0015 userToken per 1.0 validatorToken
```

That creates a bounded, structured arbitrage surface for keeping pools balanced.

### 7.3 Liquidity providers

The Fee AMM supports liquidity provision, including:

- dual-token liquidity
- single-sided validator-token liquidity
- fungible LP shares representing pool ownership

This lets stablecoin issuers, infrastructure providers, or ecosystem liquidity providers support fee usability for specific tokens.

## 8. Why the Fee AMM Is Separate from the Stablecoin DEX

Tempo has both:

- an **enshrined Stablecoin DEX**
- an **enshrined Fee AMM**

They are related, but they serve different jobs.

### Stablecoin DEX

- user-facing exchange and routing venue
- orderbook-based
- designed for trading and cross-stablecoin execution

### Fee AMM

- protocol-facing fee conversion mechanism
- fixed-rate and directional
- designed for fee settlement, validator payout, and MEV minimization

If these two systems are blurred together, Tempo's architecture becomes hard to reason about. They should be treated as adjacent but distinct layers.

## 9. Why Tempo Designed Fees This Way

This design solves several product problems at once.

### 9.1 Better payment UX

Users can hold payment assets directly and still transact.

That is much closer to the mental model of real-world payments than Ethereum's native-token gas model.

### 9.2 Better onboarding

Sponsored fees and stablecoin fee payment make it easier to onboard:

- new users
- embedded-wallet users
- passkey users
- machine-payment clients

### 9.3 Better validator flexibility

Validators do not need to require all users to pay in the same stablecoin. The fee system lets them express a receiving preference without forcing users into the same asset.

### 9.4 Better app economics

Because fees are priced in USD terms, applications can reason about costs in the same unit as their business logic.

That matters for:

- merchant payments
- remittances
- embedded finance
- API monetization
- machine-to-machine commerce

## 10. Which Upper Layers Depend on This

The fee layer directly supports several higher-level Tempo services.

### Wallets

Wallets can present:

- fee-token selection
- default fee-token preferences
- sponsored fee flows

without teaching users to manage a separate gas asset.

### Tempo Transactions

Tempo's `0x76` transaction type becomes much more useful because it can carry:

- explicit `fee_token`
- fee sponsorship via `fee_payer_signature`

So the transaction layer and fee layer reinforce each other.

### TIP-20 Stablecoins

TIP-20 tokens become more valuable inside Tempo when they can also serve as fee tokens. That is one reason issuers may care about fee-pool liquidity.

### Stablecoin payments and MPP

Payment applications and machine-payment flows benefit from:

- predictable costs
- fewer wallet setup steps
- the ability to use the same asset family for both payment and fees

## 11. The Right Mental Model

A concise way to think about Tempo fees is:

> Tempo treats transaction fees as a stablecoin-native settlement flow.

Instead of forcing users to buy a special gas coin, the chain:

- prices gas in USD terms
- lets users pay in supported stablecoins
- converts those fees for validators through a dedicated protocol AMM

That choice is not a small UX tweak. It is one of the foundations of Tempo's payments-first design.

## References

- `https://docs.tempo.xyz/protocol/fees/spec-fee`
- `https://docs.tempo.xyz/protocol/fees/spec-fee-amm`
- `https://docs.tempo.xyz/protocol/fees/fee-amm/`
- `https://docs.tempo.xyz/guide/payments/pay-fees-in-any-stablecoin`
- `https://docs.tempo.xyz/quickstart/evm-compatibility`
