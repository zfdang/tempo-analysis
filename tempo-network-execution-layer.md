# Tempo Network and Execution Layer

This document explains how Tempo's network and execution layer extends canonical Ethereum, why those extensions exist, and which higher-layer services they are designed to support.

It focuses on the **network and execution layer**, not the full Tempo stack. In particular:

- it covers consensus, blockspace, fee mechanics, execution semantics, gas accounting, and protocol-enforced system infrastructure
- it does **not** treat Tempo Transactions, TIP-20, MPP, or wallet UX as part of the same layer, even though the network layer is built to support them

Where relevant, this document maps lower-layer changes to upper-layer capabilities. Those mappings are partly explicit in Tempo's docs and partly straightforward architectural inference from the documented protocol design.

## 1. Baseline: What Tempo Keeps from Ethereum

Tempo is not a clean-room replacement for Ethereum's execution model. It keeps a large part of the Ethereum developer surface:

- EVM compatibility, targeting the **Osaka** EVM hard fork
- Solidity and standard Ethereum tooling such as Foundry and Hardhat
- Ethereum JSON-RPC compatibility
- the broad smart-contract execution model developers already know

So the right mental model is not "Tempo abandons Ethereum." It is:

- **Tempo keeps Ethereum's execution environment where possible**
- **Tempo changes the network and execution layer where payment workloads need different behavior**

## 2. Why Tempo Extends Ethereum at the Network Layer

Canonical Ethereum is a general-purpose blockchain. Tempo is trying to be a **payments-first** blockchain.

That shift in product goal changes what the lower layers must optimize for:

- faster and more deterministic settlement
- stablecoin-native fees instead of native-token gas UX
- predictable payment inclusion under congestion
- higher throughput for simple payment traffic
- lower friction for machine payments and agent workflows
- better support for stablecoin routing and fee conversion

In Ethereum, many of these concerns are left to wallets, paymasters, application contracts, bundlers, or offchain coordination. Tempo moves more of them into the chain itself.

## 3. Core Network and Execution Extensions

### 3.1 Deterministic Sub-Second Finality

#### What changes vs. Ethereum

Ethereum finality is probabilistic in the short term and relies on a slower finality path. Tempo instead uses **Simplex BFT consensus** via Commonware.

According to Tempo's public protocol docs:

- blocks are produced at roughly **600ms** under normal conditions
- finality is **deterministic**
- once a block is finalized, it is not expected to be reverted
- the validator set is initially permissioned
- proposer selection uses a **VRF** for random leader election

#### Why Tempo does this

The purpose is to make settlement behave more like payment infrastructure than like a speculative block market:

- users and services can treat finalized blocks as irreversible
- synchronous payment flows do not need to wait for many confirmations
- applications can rely on very low settlement latency

#### What upper-layer services this supports

This directly supports:

- stablecoin payments that need instant settlement certainty
- payment acceptance flows that verify transactions in near real time
- MPP request/response flows, where a paid API call cannot wait minutes for safe confirmation
- agentic commerce, where software must pay and continue a workflow immediately
- remittances, payroll, payouts, and embedded-finance applications that need fast, final settlement

### 3.2 Payment-Aware Blockspace and Payment Lanes

#### What changes vs. Ethereum

Tempo modifies the block model so payment traffic is not treated the same as all other traffic.

Its blockspace specifications introduce:

- extra header fields, including `general_gas_limit`, `shared_gas_limit`, and `timestamp_millis_part`
- a payment-lane mechanism that separates payment and non-payment gas constraints
- block validity rules that explicitly constrain non-payment transactions through `general_gas_limit`
- transaction classification rules for identifying payment transactions from transaction payload alone

Payment transactions are classified without reading blockchain state. In the current specification, a transaction is considered a payment transaction when:

- `tx.to` starts with the TIP-20 payment prefix `0x20c0000000000000000000000000`, or
- for Tempo Transactions, every entry in `tx.calls` targets an address starting with the TIP-20 payment prefix `0x20c0000000000000000000000000`

This classification works because TIP-20 tokens created through the TIP-20 Factory receive deterministic addresses that start with the payment prefix, so the protocol can identify payment transactions from transaction data alone without state lookups.

Tempo's fee spec currently describes a conservative operating model where approximately **94% of blockspace is reserved for payment transactions** and approximately **6%** is left for general computation, with room to evolve as throughput scales.

#### Why Tempo does this

Ethereum allows any sufficiently profitable activity to compete in one shared blockspace market. Tempo treats that as a bad default for payment infrastructure.

The purpose of payment lanes is to ensure:

- payment traffic is not crowded out by unrelated DeFi or complex contract activity
- payment throughput stays predictable under congestion
- fee behavior stays stable enough for payment applications

This is one of Tempo's clearest network-level departures from canonical Ethereum.

#### What upper-layer services this supports

This directly supports:

- high-volume stablecoin transfers
- merchant payments and general payment acceptance
- machine payment traffic where each call may produce a chain settlement
- per-request or per-session monetization for APIs and MCP tools
- wallet UX that depends on "payments just work" even during unrelated network demand spikes

It also indirectly supports:

- Tempo Transactions, because batching and sponsorship are much more useful when payment traffic has protected blockspace
- TIP-20 payment flows, because payment lanes are explicitly built around payment transaction classification

### 3.3 Extended Block Format and System Transactions

#### What changes vs. Ethereum

Tempo extends the Ethereum block format in multiple ways:

- new header scalars for blockspace partitioning and sub-second timestamps
- system transactions at the start and, when required, the end of blocks
- protocol-defined ordering constraints for those system transactions

The public blockspace spec explicitly calls out:

- a **Rewards Registry** system transaction at the start of each block
- block-body sections for proposer-lane transactions, shared-gas transactions, and protocol-defined end-of-block transactions

The docs also describe system transactions being used for protocol operations such as the fee system and related machinery.

#### Why Tempo does this

Ethereum block bodies are mostly a list of user transactions. Tempo needs more protocol-managed structure because payment infrastructure needs protocol-enforced housekeeping.

These extensions let Tempo:

- maintain validator reward metadata
- support protocol fee operations
- coordinate specialized payment-aware blockspace behavior
- expose sub-second timing more precisely than whole-second timestamps

#### What upper-layer services this supports

This supports, mostly indirectly:

- stable fee settlement and validator payout flows
- payment-lane guarantees
- protocol-level stablecoin fee conversion
- better timing behavior for synchronous payment and service-verification flows

### 3.4 No Native Gas Token and USD-Denominated Fees

#### What changes vs. Ethereum

Ethereum requires a native gas asset. Tempo does not.

Tempo's fee system changes the fee model in several important ways:

- there is **no native gas token**
- transaction fees are paid in **USD-denominated TIP-20 stablecoins**
- fee accounting is denominated in **attodollars** per gas
- the base fee is **fixed**, not dynamically adjusted like Ethereum's EIP-1559 base fee
- priority fees still exist for faster inclusion
- fee-token selection is built into protocol logic

Tempo's public fee docs say the fixed base fee is chosen so that a TIP-20 transfer costs **less than $0.001**.

As specified in TIP-1010, the current mainnet gas parameters are:

- base fee: **20 billion attodollars per gas** (2 × 10^10)
- total block gas limit: **500M gas**
- general gas limit: **30M gas** per block

A standard TIP-20 transfer (~50,000 gas) costs approximately 1,000 microdollars (0.1 cent / $0.001) at the base fee.

#### Why Tempo does this

The purpose is to make transaction costs behave like payment infrastructure:

- users pay in the same class of assets they are already using for payments
- applications can reason about costs in USD terms
- operators avoid the UX and treasury complexity of requiring a volatile native token for gas

This is one of Tempo's most important execution-layer changes because it affects every transaction on the chain.

#### What upper-layer services this supports

This directly supports:

- stablecoin payments without separate gas-token onboarding
- wallet flows that can present fees in familiar dollar terms
- business applications that need predictable unit economics
- sponsored transactions and gasless onboarding
- MPP clients that only need stablecoins rather than a second native asset

It also supports broader application categories explicitly highlighted in Tempo's docs:

- global payouts
- remittances
- payroll
- embedded finance
- micropayments

### 3.5 Fee Manager and Fee AMM as Protocol-Level Infrastructure

#### What changes vs. Ethereum

Ethereum does not include a native stablecoin fee-conversion system. Tempo does.

Tempo's protocol docs describe:

- a **Fee Manager** system contract
- a **Fee AMM** that converts between a user's chosen stablecoin and the validator's preferred stablecoin
- automatic reservation of fee liquidity during transaction validation
- atomic max-fee deduction and refund logic

The Fee AMM is deliberately specialized:

- fee swaps occur at fixed rates
- the design aims to minimize MEV
- the protocol can collect fees in many stablecoins while still paying validators in their preferred stablecoin

#### Why Tempo does this

Without a native gas token, a stablecoin fee model needs a protocol answer to the question:

"What if the payer wants to spend token A, but the validator wants token B?"

Tempo solves that at the execution layer instead of punting it to wallet heuristics or external fee relayers.

The purpose is to:

- make "pay fees in any supported stablecoin" actually workable
- reduce user friction
- keep validator incentives intact
- prevent fee-conversion logic from turning into a large MEV surface

#### What upper-layer services this supports

This directly supports:

- fee payment in any supported stablecoin
- wallet-level fee-token preferences
- stablecoin-native transaction submission
- sponsored transaction flows where the sponsor chooses the fee token

It also indirectly supports:

- broader payment acceptance, because wallets do not need to force all users into one stablecoin
- cross-stablecoin commerce, because fee conversion is built into the lower layer

### 3.6 Enshrined Stablecoin Exchange and System Contracts

#### What changes vs. Ethereum

Ethereum does not ship with a chain-native stablecoin exchange layer. Tempo does.

Its public docs describe predeployed system contracts including:

- **TIP-20 Factory**
- **Fee Manager**
- **Stablecoin DEX**
- **TIP-403 Registry**
- **pathUSD**

This is not just "an ecosystem app happens to exist." These contracts are part of the protocol surface that Tempo expects builders to use.

#### Why Tempo does this

Payments often fail in practice not because transfers are hard, but because:

- users hold different assets
- fee flows need conversion
- payment assets need canonical system support
- policy and asset semantics need to be shared across applications

By enshrining key stablecoin and fee infrastructure, Tempo reduces fragmentation in the execution environment.

#### What upper-layer services this supports

This supports:

- stablecoin issuance
- cross-stablecoin payment routing
- onchain FX and exchange
- application flows where payer and payee do not use the same stablecoin
- compliance-aware stablecoin infrastructure

### 3.7 VM Semantics for a No-Native-Token Chain

#### What changes vs. Ethereum

Because Tempo has no native token, some Ethereum VM assumptions no longer hold.

Tempo's public docs explicitly call out:

- `BALANCE` and `SELFBALANCE` return `0`
- `CALLVALUE` returns `0`
- applications should use TIP-20 `balanceOf` instead of native-balance assumptions

Tempo also documents a wallet-facing compatibility quirk:

- `eth_getBalance` returns a very large sentinel value rather than a meaningful native-token balance

This is a compatibility shim for wallet behavior, not a sign that a real native gas asset exists.

#### Why Tempo does this

The purpose is to preserve developer compatibility while removing the native-token requirement.

Tempo wants:

- contracts and tooling to remain EVM-oriented where possible
- wallets to avoid blocking transactions on missing "ETH"
- applications to move toward TIP-20 balances for actual payment logic

#### What upper-layer services this supports

This supports:

- wallet compatibility during migration from Ethereum assumptions
- stablecoin-first account UX
- onboarding flows where users can transact without ever holding a native gas asset

### 3.8 Higher State-Creation Costs

#### What changes vs. Ethereum

Tempo significantly increases the gas costs of creating permanent state, as described in TIP-1000.

Examples from the public docs:

- new storage slot creation: **250,000 gas** instead of Ethereum's **20,000**
- account creation: **250,000 gas**
- contract creation code storage: much higher than Ethereum's standard model

#### Why Tempo does this

Tempo's public rationale is explicit: high throughput creates a greater risk of large-scale state growth attacks.

If the chain is optimized for very high payment throughput, an attacker could otherwise create enormous amounts of permanent state cheaply and permanently degrade database performance.

So the purpose is:

- economic protection against state-bloat spam
- preserving long-term chain performance
- keeping payment throughput from becoming a vector for infrastructure degradation

#### What upper-layer services this supports

This is mostly a defensive extension, but it still supports higher layers by protecting:

- long-term performance for payment applications
- reliability for wallets and service operators
- sustainable operation of high-throughput payment and agent ecosystems

### 3.9 Storage-Creation Gas Exempt from Protocol Limits

#### What changes vs. Ethereum

Tempo's TIP-1016 introduces a subtle but important change:

- storage-creation gas still exists
- users still pay for it
- but storage-creation gas does **not** count against protocol execution limits

The docs split gas into:

- **execution gas**, which counts toward protocol limits
- **storage creation gas**, which does not count toward protocol limits but still counts toward the user's `gas_limit`

#### Why Tempo does this

This solves a Tempo-specific problem created by the higher state-creation pricing.

Without this change:

- new-account transfers would drastically reduce effective throughput
- larger contracts would become difficult to deploy
- payment throughput would suffer whenever flows touched new accounts

Tempo's own docs quantify the result as roughly a **4x throughput improvement for new-account transfers** under the payment-lane model.

So the purpose is to get both:

- strong protection against state growth
- high throughput for payment-heavy workloads

#### What upper-layer services this supports

This directly supports:

- payments to newly created recipient accounts
- large-scale onboarding of new users
- payment apps that regularly pay fresh addresses
- stablecoin issuance and distribution patterns

It also matters for:

- payroll and payout systems
- remittances
- marketplace settlement
- machine-payment onboarding where recipients or service accounts may be newly initialized

## 4. What Tempo's Network Layer Is Optimizing For

Across all of the changes above, Tempo is optimizing for a different operating model than canonical Ethereum.

The lower layer is designed to make these properties true:

- settlement is fast enough for synchronous applications
- payment traffic remains available under congestion
- fees stay stable and denominated in dollars
- users do not need a native gas token
- validators can still be paid in a sensible, protocol-managed way
- state growth is expensive, but payment throughput remains high

That combination is not accidental. It is the network-and-execution counterpart to Tempo's broader product positioning as a payments-first chain.

## 5. Which Higher Layers Depend on These Extensions

The network and execution layer does not exist in isolation. It is clearly designed to support specific higher layers.

### 5.1 Transaction Layer

Even though Tempo Transactions belong to a higher layer than the raw network, they depend on network-layer features such as:

- stablecoin-native fee handling
- sponsorship-compatible fee settlement
- protected payment blockspace
- sub-second finality

Without those lower-layer choices, Tempo Transactions would be less useful as a payment-native transaction format.

### 5.2 Asset and Stablecoin Layer

The network layer supports the asset layer by making stablecoins first-class operational assets rather than just ERC-20-like contracts floating in a native-gas environment.

This supports:

- TIP-20 payments
- stablecoin fee payment
- memos and reconciliation flows
- stablecoin issuance and management
- policy-aware asset behavior

### 5.3 Wallet and Identity Layer

Tempo's network model directly improves wallet UX:

- no native gas token to manage
- support for gasless or sponsored flows
- predictable fees in dollar units
- faster perceived settlement

This is a major reason Tempo can push a more consumer-friendly account model.

### 5.4 Machine Payments Layer

The machine-payments docs make the dependency especially clear. Tempo explicitly positions its network around:

- roughly **600ms** block production and deterministic finality for synchronous request/response payment flows
- low enough fees for micropayments
- fee sponsorship so clients can hold stablecoins instead of a separate gas token
- high throughput for payment-channel settlement volume

That directly supports:

- one-time paid API calls
- session-based billing
- streamed payments
- MCP tool monetization
- agent-to-service payment flows

### 5.5 Application Layer

At the application layer, the same lower-layer design supports broader product categories that Tempo highlights publicly:

- stablecoin payments
- point-of-sale-style instant settlement
- global payouts
- remittances
- payroll
- embedded finance
- micropayments
- agentic commerce

## 6. Summary Table

| Tempo extension | What changes vs. Ethereum | Primary purpose | Higher-layer services enabled |
|---|---|---|---|
| Simplex BFT + deterministic finality | Replaces slower probabilistic short-term settlement with fast BFT finality | Make settlement payment-grade | Stablecoin payments, MPP, instant verification, agent flows |
| Payment lanes and extra blockspace fields | Splits payment and non-payment capacity | Keep payment traffic predictable under congestion | Transfers, payment APIs, machine payments, wallet reliability |
| Extended block structure and system transactions | Adds protocol-managed block sections and system operations | Coordinate payment-aware protocol behavior | Fee operations, rewards, payment-lane guarantees |
| No native gas token | Removes native-token gas dependency | Make the chain stablecoin-native | Wallet onboarding, business payments, gasless UX |
| USD-denominated fixed fee model | Replaces volatile native-token fee exposure with dollar-based pricing | Predictable unit economics | Stablecoin apps, micropayments, enterprise budgeting |
| Fee Manager + Fee AMM | Adds protocol fee conversion between stablecoins | Let users pay fees in many stablecoins while validators receive preferred assets | Any-supported-stablecoin fees, sponsorship, cross-token UX |
| Enshrined system contracts | Adds predeployed stablecoin and fee infrastructure | Reduce fragmentation and standardize payment primitives | TIP-20 issuance, stablecoin DEX, policy-aware payments |
| No-native-token VM semantics | `BALANCE`/`SELFBALANCE`/`CALLVALUE` assumptions change | Preserve EVM compatibility without fake native asset semantics | Wallet compatibility, stablecoin-first UX |
| Higher state-creation costs | New storage and account creation are far more expensive | Defend against state-growth spam | Long-term reliability for high-throughput payment workloads |
| Storage gas exempt from protocol limits | Users still pay storage cost, but block execution limits track execution only | Preserve throughput while keeping state expensive | New-account payments, payouts, onboarding-heavy systems |

## 7. Bottom Line

Tempo's network and execution layer extends Ethereum in a very specific direction: not toward maximal generality, but toward **stablecoin-native, payment-first execution**.

The main extensions are:

- deterministic sub-second finality
- payment-protected blockspace
- stablecoin-native fees with no gas token
- protocol fee conversion and exchange infrastructure
- execution-layer adaptations for a no-native-token environment
- gas-accounting changes that defend against state bloat without sacrificing payment throughput

The purpose of these extensions is not abstract protocol novelty. It is to make the lower layer usable for the upper services Tempo cares about:

- stablecoin payments
- gasless onboarding
- payment-native transactions
- machine-payable APIs
- streaming and session payments
- embedded-finance and payout products
- agentic commerce

In short:

- Ethereum gives Tempo a familiar execution foundation
- Tempo extends the network and execution layer so that payments become a first-class systems property rather than just an application pattern

## References

- [EVM Differences](https://docs.tempo.xyz/quickstart/evm-compatibility)
- [Blockspace Overview](https://docs.tempo.xyz/protocol/blockspace/overview)
- [Payment Lane Specification](https://docs.tempo.xyz/protocol/blockspace/payment-lane-specification)
- [Consensus and Finality](https://docs.tempo.xyz/protocol/blockspace/consensus)
- [Fee Specification](https://docs.tempo.xyz/protocol/fees/spec-fee)
- [Fee AMM Specification](https://docs.tempo.xyz/protocol/fees/spec-fee-amm)
- [TIP-1000: State Creation Cost Increase](https://docs.tempo.xyz/protocol/tips/tip-1000)
- [TIP-1016: Exempt Storage Creation from Gas Limits](https://docs.tempo.xyz/protocol/tips/tip-1016)
- [Predeployed Contracts](https://docs.tempo.xyz/quickstart/predeployed-contracts)
- [Stablecoin Payments](https://docs.tempo.xyz/guide/payments/)
- [Machine Payments](https://docs.tempo.xyz/guide/machine-payments/)
- [Accept One-Time Payments](https://docs.tempo.xyz/guide/machine-payments/one-time-payments)
