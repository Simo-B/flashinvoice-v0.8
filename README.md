# ⚡ FlashInvoice v0.8.1

**The Agnostic L402 Micro-Payment Gateway for Autonomous AI Agents**

FlashInvoice allows AI agents and autonomous systems to pay each other instantly using the Lightning Network and the L402 standard — with zero human intervention, no passwords, and no KYC.

Built for the **machine-to-machine (M2M) economy** of 2026 and beyond.

---

## Why FlashInvoice?

Traditional payment systems (Stripe, Visa, PayPal) were designed for humans. They fail at scale for autonomous agents because of:

- High fixed fees
- Slow settlement
- Need for human identity (KYC)

**FlashInvoice** solves this with:
- Lightning Network (instant + near-zero fees)
- L402 standard (native HTTP payment protocol)
- Nostr public keys (decentralized, zero-trust identity)

---

## Quick Start

### 1. Call the API directly (No SDK required)

```bash
curl -X POST https://flashinvoice.xyz/create-invoice \
  -H "Content-Type: application/json" \
  -d '{
    "agent_pubkey": "npub1youragentpubkey...",
    "task_hash": "unique_task_identifier_123",
    "amount_usd": 0.05,
    "description": "Translation service"
  }'
You will receive an HTTP 402 Payment Required response containing the Bolt11 invoice.

Key Features

L402 Native — Full support for HTTP 402 + WWW-Authenticate header
Nostr Authentication — Agents authenticate using public key signatures
Idempotent & Replay Protected — Safe against aggressive bot retries
Provider Agnostic — Switch between LNBits, OpenNode, Voltage, etc. via config
Stateless Architecture — No sessions, no user accounts, minimal data storage
AI-First Design — Optimized for autonomous agents and multi-agent systems


Environment Variables








































VariableDescriptionRequiredSUPABASE_URLSupabase project URLYesSUPABASE_KEYSupabase anon/public keyYesLIGHTNING_PROVIDERlnbits (default) or opennodeYesLNBITS_API_KEYRequired only if using LNBitsConditionalLNBITS_URLLNBits API endpointConditionalNOSTR_PRIVATE_KEYUsed to sign outgoing webhooksYes

llms.txt – For AI Agents & Coding Assistants
FlashInvoice includes a llms.txt file at the root of the project. This file is specifically designed so that autonomous coding agents (Cursor, Windsurf, Claude, GPT-4o, etc.) can understand and integrate the API without human help.
You can access it here:
https://flashinvoice.xyz/llms.txt

API Endpoints

























MethodEndpointDescriptionPOST/create-invoiceRequest a new L402 invoicePOST/webhook/lnbitsConfirm Lightning paymentGET/healthHealth check

Roadmap

 L402 + Nostr Authentication
 Idempotency & Replay Protection
 Provider Abstraction (LNBits + future providers)
 Agent Reputation Scoring (v0.9)
 Official Python + TypeScript SDK
 Agent Marketplace


Links

Live Demo: https://flashinvoice.xyz
GitHub: github.com/yourusername/flashinvoice
X (Twitter): @flashinvoice
Documentation: Coming soon


License
MIT
