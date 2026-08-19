---
name: salesforce-demo-prep
description: "Populate Salesforce orgs for manager demos — check org capacity, insert standard objects, add minimal custom objects, and structure the demo flow."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, demo, dev-edition, standard-objects, manager-demo]
---

# Salesforce Demo Prep — Populating Salesforce for Manager Demos

## The Problem
When preparing a Salesforce org for a manager demo, the Developer Edition org quickly hits its limits:
- **Max 10 custom objects** — deploy fails silently with "reached maximum number of custom objects"
- **Apex deployment restricted** — "Not available for deploy for this organization"
- **Metadata errors** — XML syntax errors prevent deployment

## The Fix: Populate Standard Objects First

### Step 1: Check Org Capacity
```bash
# Before deploying anything, check what's already in the org
sf data query --query "SELECT Id, Name FROM Account LIMIT 1"
sf data query --query "SELECT COUNT() cnt FROM Account"
```

### Step 2: Insert Standard Data (Always Available)
Standard objects are always available — no custom object deployment needed:

| Object | Use For | Demo Value |
|--------|---------|------------|
| **Account** | Companies | Fake companies across industries |
| **Contact** | People | 3 contacts per account |
| **Opportunity** | Deals | Full pipeline (outreach → closing) |
| **Quote** | Proposals | Fake quotes with products/pricing |
| **Order** | Actual orders | Line items linked to quotes/opportunities |
| **Case** | Support | Post-sales support tickets |
| **Campaign** | Marketing | Lead sources and events |

### Step 3: Insert Data via CSV
```bash
# Create CSV with standard fields only
sf data insert --sobject Account --data-file accounts.csv
sf data insert --sobject Contact --data-file contacts.csv
sf data insert --sobject Opportunity --data-file opportunities.csv
```

### Step 4: Add One Custom Object (If Needed for Demo)
Only after standard data is in, add ONE custom object manually via UI:
1. Setup → Object Manager → Create Custom Object
2. Name it `Product` or `Contract` (singular)
3. Add 3-4 fields max
4. Insert 5-10 records via UI or CSV

## Demo Flow for Manager
1. "Here are our companies" → Accounts list
2. "Here's our active pipeline" → Opportunities with stages
3. "Here are the deals in negotiation" → Filtered Opportunities
4. "Here are the closed deals" → Closed Won opportunities
5. "Here's the contract for this deal" → Custom object example
6. "Here's the post-sales support" → Cases linked to accounts

## Pitfalls
- **Don't deploy metadata first** — check org capacity before deploying
- **Don't assume empty = ready** — org may have hit custom object limits
- **Don't skip standard objects** — they're the backbone of any demo
- **Don't over-engineer** — one custom object is enough for a demo