# Tempo Stablecoin DEX and FX Layer

## Overview

Tempo includes an **enshrined Stablecoin DEX** as part of the protocol stack.

That matters because Tempo is not just trying to host stablecoins. It is trying to make them usable across:

- payments
- wallet balances
- merchant settlement
- fee-token ecosystems
- machine-payment workflows

If multiple stablecoins exist on the chain, Tempo needs a native answer to one question:

> How does value move cleanly between those stablecoins without forcing every application to depend on an external exchange?

The Stablecoin DEX is Tempo's answer.

## 1. What This Layer Is

Tempo's Stablecoin DEX is a protocol-level exchange for trading between TIP-20 stablecoins.

According to the specification, it is:

- a singleton contract
- deployed at `0xdec0000000000000000000000000000000000000`
- currently scoped to **USD-denominated TIP-20 stablecoins**
- built as an **onchain orderbook**, not a constant-product AMM

This makes it different from many EVM ecosystems, where routing and stablecoin exchange are usually pushed into external DeFi protocols.

## 2. Why Tempo Includes an Enshrined Exchange

Tempo is a payments-first chain. That pushes exchange closer to the protocol for several reasons.

### 2.1 Stablecoin fragmentation is a payments problem

If one app pays in one stablecoin, another settles in another, and fees or treasury balances sit in a third, then conversion stops being a trading niche and becomes basic infrastructure.

### 2.2 Payment routing needs predictability

Tempo wants applications to reason about:

- the route between stablecoins
- the quality of execution
- the existence of usable liquidity

An enshrined exchange makes that easier to standardize.

### 2.3 Stablecoin liquidity should not be scattered across too many pairs

The DEX is designed to reduce liquidity fragmentation rather than maximize pair proliferation.

That is a very payment-oriented design goal.

## 3. What Tempo Means by "FX"

In a Tempo context, "FX" should be read carefully.

Today, the protocol documentation describes:

- stablecoin-to-stablecoin trading
- currently only for USD-denominated TIP-20 tokens
- deterministic routing between those stablecoins

So Tempo's current FX layer is best understood as:

> a protocol-native stablecoin conversion and routing layer

It is **not** yet a general-purpose, all-currency foreign-exchange system in the traditional sense.

## 4. Core Market Structure

The most distinctive part of the DEX is its **quote-token tree**.

### 4.1 Each token has one quote token

Every TIP-20 token specifies a single `quoteToken()`.

That means:

- a token does not trade against arbitrary many other assets
- it trades against one designated quote token
- routes between tokens are determined by these quote-token relationships

### 4.2 The graph is constrained into a tree

The exchange design requires:

- each token picks a single quote token
- quote-token relationships do not form cycles

This creates a tree-like structure with a crucial consequence:

> there is only one path between any two supported stablecoins

That sharply reduces routing ambiguity and liquidity fragmentation.

### 4.3 `pathUSD` as a neutral anchor

Tempo provides `pathUSD` as a neutral USD stablecoin option for quote-token relationships.

Its role is architectural as much as economic:

- it can serve as a common routing anchor
- it gives issuers a default place to connect
- it helps maintain the tree structure

## 5. Execution Model

Tempo's DEX is not an AMM-first design. It is an **orderbook** with price-time priority.

### 5.1 Discrete ticks and price-time priority

Orders rest at discrete price ticks.

The system maintains:

- best bid
- best ask
- FIFO priority within a tick

That gives Tempo a more explicit market structure than a pool-only AMM model.

### 5.2 Immediate swaps against the active book

Swaps execute immediately against the best available orders:

- selling base for quote walks down the bid side
- selling quote for base walks up the ask side

If the two tokens are not directly paired, the DEX uses the unique quote-token path and performs a multi-hop swap.

### 5.3 Internal balances

The DEX maintains internal user balances per token.

That lets it:

- escrow funds for orders
- credit maker proceeds internally
- reduce repeated token movement overhead
- support more efficient trading workflows

### 5.4 Flip orders

Tempo also supports **flip orders**.

A flip order behaves like a resting order until it is fully filled. Once fully filled, it can recreate itself on the opposite side at a configured `flipTick`.

This is a notable protocol feature because it supports recurring liquidity strategies without forcing the user to manually repost each time.

## 6. Why Tempo Chose This Design

The DEX specification points to several motives.

### 6.1 Better execution for stablecoin pairs

Tempo is optimizing for cross-stablecoin execution, not for highly speculative long-tail asset trading.

### 6.2 Lower routing ambiguity

Because only one route exists between any two supported tokens, applications do not need to compare many routing graphs or fragmented pools.

### 6.3 Lower liquidity fragmentation

Instead of spreading liquidity across many overlapping pairs, the quote-token model concentrates it.

### 6.4 Lower mid-block MEV surface

The specification explicitly frames the design as a way to provide deterministic stablecoin execution while reducing unnecessary chain load and mid-block MEV surface.

## 7. What This Layer Enables Above It

The DEX is not an isolated trading venue. It supports higher layers of the Tempo stack.

### 7.1 Cross-stablecoin payments

Applications can accept or settle in different Tempo-native stablecoins while still having a built-in conversion layer available onchain.

### 7.2 Wallet asset routing

Wallets can reason about:

- which stablecoin the user holds
- which stablecoin a destination wants
- which route exists between them

without depending on an external routing universe.

### 7.3 Stablecoin issuer interoperability

Issuers are not only creating isolated assets. They are joining a structured exchange graph.

That helps Tempo function more like a payment network than a collection of unrelated tokens.

### 7.4 Merchant and treasury operations

Merchants, platforms, and treasury operators may receive one stablecoin and prefer another. The DEX gives Tempo a protocol-native place for that conversion.

## 8. Stablecoin DEX vs. Fee AMM

These two layers are easy to confuse, but they are not the same.

| Layer | Main job | Market model | Primary users |
|---|---|---|---|
| Stablecoin DEX | User-facing stablecoin exchange and routing | Orderbook with ticks and price-time priority | Traders, wallets, payment apps, issuers |
| Fee AMM | Protocol fee conversion between payer token and validator token | Fixed-rate directional AMM | The protocol, validators, rebalancers, LPs |

The DEX helps users and apps exchange assets.

The Fee AMM helps the protocol settle transaction fees.

## 9. Current Scope and Limits

Tempo's DEX is intentionally narrower than a generic DeFi exchange.

Based on the current specification:

- only USD-denominated TIP-20 tokens are supported today
- non-USD cross-currency trading is not currently supported
- same-currency trading for non-USD tokens is not currently supported
- routing is intentionally constrained to the unique quote-token path

That narrow scope is a design choice, not an omission by accident.

## 10. The Right Mental Model

A concise way to think about Tempo's exchange layer is:

> Tempo enshrines stablecoin conversion because payment infrastructure needs a native routing layer.

The Stablecoin DEX is therefore not just "another DeFi app." It is part of Tempo's payment architecture:

- assets can be issued as TIP-20 tokens
- routed through a deterministic exchange graph
- used in payments, treasury flows, and application settlement

That is why the DEX belongs in a full explanation of Tempo.

## References

- `https://docs.tempo.xyz/protocol/exchange/spec`
- `https://docs.tempo.xyz/protocol/exchange/quote-tokens`
- `https://docs.tempo.xyz/protocol/exchange/executing-swaps`
- `https://docs.tempo.xyz/protocol/exchange/providing-liquidity`
- `https://docs.tempo.xyz/protocol/exchange/exchange-balance`
