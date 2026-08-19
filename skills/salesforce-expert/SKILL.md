---
name: salesforce-expert
description: "Deep expertise in Salesforce platform architecture, editions, clouds, AI (Agentforce/Einstein), automation tools, APIs, integrations, and certification paths."
version: 1.0.0
author: Hermes Agent + Research compiled July 2026
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, crm, platform, agentforce, einstein, data-cloud, admin, developer, architecture, trailhead, certifications]
---

# Salesforce Platform — Complete Expert Reference

## What Is Salesforce?

Salesforce is a **cloud-based CRM (Customer Relationship Management)** platform that provides the entire technology stack for managing customer interactions — from lead generation through post-sale support. It's not just one product but a **platform** with multiple "Clouds" and an underlying metadata-driven architecture.

### Core Identity
- Founded: 1999 by Marc Benioff
- Model: SaaS (Software as a Service) — everything runs in the cloud
- Multi-tenant architecture: All customers share infrastructure but are logically isolated
- Metadata-driven: Everything is configuration/metadata, not custom code

## Salesforce Editions

| Edition | Price (approx) | Key Features |
|---------|---------------|--------------|
| Essentials | $25/user/month | Basic Sales Cloud — leads, contacts, accounts. Small teams. |
| Professional | ~$80/user/month | Adds workflow automation, reports/dashboards, custom objects. |
| Enterprise | ~$165/user/month | Full customization: Apex, APIs, sandboxes. Standard for most companies. |
| Unlimited | ~$300+/user/month | Everything in Enterprise + unlimited apps, 24/7 support. |

### Salesforce Developer Edition (FREE)
- Full-featured org at zero cost with limited storage (~1GB)
- Apex, Lightning Web Components, APIs all enabled
- Never expires — perfect for development and learning
- Signup: https://developer.salesforce.com/signup

## The Clouds (Product Family)

### Sales Cloud
Leads to Contacts to Accounts to Opportunities pipeline management. Einstein AI for predictive lead scoring. Territories, price books, CPQ.

### Service Cloud
Case management, knowledge base, omni-channel routing, live chat, telephony integration. Entitlements and SLAs.

### Marketing Cloud
Email campaigns, journey builder (multi-step customer journeys), social media publishing, audience segmentation using Data Cloud data.

### Commerce Cloud
B2B/B2C storefronts with cart checkout and product catalog. Headless commerce API for custom storefronts.

### Experience Cloud
Customer portals, partner communities, supplier networks. Self-service knowledge bases connected to internal CRM data.

### Tableau (Analytics & BI)
Visual dashboards, data exploration, self-service analytics embedded in Salesforce.

### Slack (Team Communication)
Customer 360 context within channels and DMs. Workflow automation between Slack and Salesforce.

## AI: Einstein & Agentforce

### Einstein AI
- Predictive analytics — lead scoring, opportunity insights, case classification
- Next-best-action recommendations for reps and agents
- Einstein GPT — generative AI for summarization, drafting, Q&A within Salesforce
- Add-on to Enterprise/Unlimited editions ($50/user/month+)

### Agentforce (Autonomous AI Agents Platform)
Build and deploy autonomous AI agents that work across CRM data via Data Cloud. Key concepts:
- **Agent** — autonomous AI worker with defined role and capabilities
- **Authoring Bundle** — blueprint containing the Agent Script (.agent file) defining topics, actions, routing
- **Data Library** — knowledge source grounding agent responses
- **MCP Server** — external tool/server agents connect to (databases, APIs)
- **AgentExchange** — marketplace of pre-built agents from partners

## Data Cloud
Unified data layer connecting all Salesforce clouds. Ingests customer data from any source into a single Customer 360 profile per person/company. Powers Einstein AI and Agentforce with live data context.

## Platform Architecture

### Data Model
Organization → Schemas → Objects → Records → Fields/Relationships

| Concept | Description |
|---------|-------------|
| Object | Table/entity — Account, Contact, Opportunity, or custom Project__c |
| Field | Column within an object (text, number, date, lookup) |
| Record | A single row — specific Account, Contact etc. |

#### Relationship Types
- **Lookup** — loose reference between records
- **Master-Detail** — tight parent-child with ownership cascade and roll-up summaries
- **Many-to-Many** — junction object connecting two master-detail relationships
- **Hierarchy** — self-referencing lookup (Employee to Manager chain)
- **External Lookup** — reference to external system record via External ID

### Standard Objects
Account (companies), Contact (people at accounts), Opportunity (deals), Lead (prospects), Case (support tickets), Campaign, User, Task/Event.

### Custom Objects
Any object you create always suffixed with __c. Follow same rules as standard objects.

## Automation & Development Layers

### Layer 1: Declarative (No Code)
Page Layouts, Record Types, Validation Rules, Approval Processes, Flow (Autopilot — #1 tool for admins)

### Layer 2: Programmatic (Code)
| Tool | Language | Purpose |
|------|----------|---------|
| Apex | Java-like class-based language | Business logic, triggers, controllers |
| SOQL | SQL-like query language | Query records from the database |
| SOSL | Full-text search | Search across multiple objects simultaneously |
| DML | INSERT/UPDATE/DELETE/UPSERT/MERGE | CRUD operations on records |
| Lightning Web Components (LWC) | JavaScript web components | Custom UI in Lightning Experience |

### Layer 3: Events & Integration
Platform Events (pub/sub messaging), Change Data Capture, Outbound Message (SOAP webhook), Callouts (Apex calling external APIs)

Golden Rule: Declarative First, Code Second.

## API Ecosystem
| API | Use Case |
|-----|----------|
| REST API | Modern integrations — JSON-based, most commonly used |
| SOAP API | Enterprise integrations needing strict contracts |
| Bulk API 2.0 | Large data loads (millions of records) async |
| Streaming/Pub-Sub API | Real-time event notifications WebSocket/SSE |
| Tooling API | Deploy metadata programmatically — used by CI/CD tools like sf CLI |

## SF CLI (`sf`) — Installed v2.144.6

Key Commands:
sf org login web — Interactive browser login to your org
sf org list — Show all authenticated orgs
sf project generate --name my-project — Create DX project structure
sf project deploy start — Deploy to default org
sf dev push — Push local source to org
sf apex test run --result-format human — Run Apex tests

## Certifications & Learning Path (Trailhead)
- Admin Track: Fundamentals → Certified Administrator → Platform App Builder
- Developer Track: Platform Developer I → Platform Developer II
- Architect Track: System Architecture → Application → Integration → Data
- AI/Agentforce Track: Certified Agentforce Specialist → Architect
- Learning: https://trailhead.salesforce.com — free hands-on exercises with real orgs.

## Practical Tips
1. Always use sf CLI never deprecated sfdx commands
2. Declarative before code — try Flow first, Apex only when necessary
3. SOQL is not SQL — no JOINs; traverse relationships via dot notation (Account.Name)
4. Governor limits: 100 SOQL queries/scope, 10K records DML/scope
5. Minimum 75% Apex code coverage required for prod deployment
6. Scratch orgs for dev work — ephemeral clean reproducible environments