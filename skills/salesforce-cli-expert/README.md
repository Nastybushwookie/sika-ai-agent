---
name: salesforce-cli-expert
version: 1.0.0
author: Hermes Agent + Research compiled from official sources
platforms: [linux, macos, windows]
tags:
  - salesforce
  - cli
  - sf
  - sfdx
  - agentforce
  - devops
  - ci-cd
  - automation
  - ai-agents
  - plugin-agent
  - sf-skills
description: Complete expert reference for Salesforce CLI (sf) including installation, authentication, org management, Agentforce plugin commands, CI/CD patterns, and AI agent integration. Covers official Salesforce repositories: salesforcecli/plugin-agent, forcedotcom/sf-skills, and all sf command categories.
---

# Salesforce CLI Expert Skill — Documentation & Usage Guide

## Overview

This skill provides comprehensive expertise in the **Salesforce CLI (sf)** for development, automation, and AI agent integration. It was compiled from official Salesforce repositories, documentation, and community resources through a systematic research process.

---

## Research Process

### Sources Consulted
1. **Official Salesforce CLI Page**: https://developer.salesforce.com/tools/salesforcecli
2. **Command Reference**: https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/
3. **Setup Guide PDF**: https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/sfdx_setup.pdf
4. **GitHub Repositories**:
   - `salesforcecli/plugin-agent` — Official Agentforce plugin with 45+ commands
   - `forcedotcom/sf-skills` — Curated skills collection for AI tools
   - `forcedotcom/cli` — Core CLI repository
   - `salesforce/agentscript` — Programmatic agent workflows
   - `salesforce/sf-pi` — API-native Apex lifecycle workflows
5. **Community Resources**: Salesforce Ben, AWS Plain English, Atrium tutorials

### Methodology
1. Scraped official plugin-agent README for all command documentation (2,457 lines)
2. Analyzed sf-skills repository structure and skill specifications
3. Extracted CI/CD patterns from GitHub Actions workflows
4. Compiled authentication methods, org management commands, and deployment flows
5. Documented Agentforce AI agent lifecycle management commands
6. Synthesized into comprehensive expert reference (21,915 bytes)

---

## What This Skill Covers

### 1. Installation & Setup
- npm installation (cross-platform)
- Homebrew (macOS/Linux)
- Windows download options
- Verification and basic commands

### 2. Project Structure
- `.sfdx-project.json` configuration
- Directory structure (force-app/main/default/...)
- Scratch org definition files

### 3. Authentication Methods (5 Types)
- Web login (interactive browser-based OAuth)
- Username/password (CI/CD with security tokens)
- JWT Bearer Flow (service-to-service, recommended for CI/CD)
- Access Token (direct OAuth token usage)
- IP Allowlist (no auth command needed if configured in org)

### 4. Org Management
- Scratch org creation and lifecycle
- DevHub configuration
- Common org commands (list, open, delete, set-default)

### 5. Project Workflows
- Deploy & retrieve metadata
- Source push/pull synchronization
- Testing execution (Apex tests, code coverage)

### 6. Agentforce Plugin Commands (45+ commands)
The official `@salesforce/plugin-agent` package provides:

#### Data Library Management (ADL)
- Create SFDRIVE/KNOWLEDGE/RETRIEVER libraries
- Upload and manage files
- Monitor indexing status

#### Agent Lifecycle
- Create agents from spec files
- Activate/deactivate published agents
- Generate agent specs with AI

#### Authoring Bundles & Agent Script
- Generate authoring bundles from specs
- Validate Agent Script compilation
- Publish to org (creates Bot, BotVersion metadata)

#### Programmatic Preview Sessions
- Start/send/end sessions for CI/CD
- Test agents programmatically

#### Testing Framework
- Generate test specs (YAML format)
- Run tests with rich evaluation (8+ evaluator types)
- Get results in human/json/junit/tap formats

#### MCP Server Management
- Register external MCP servers
- List/fetch/update/delete servers and assets

### 7. CI/CD Integration Patterns
- GitHub Actions workflows with JWT authentication
- OIDC-based authentication (modern, no RSA keys)
- Automated scratch org management
- Agent deployment pipelines

### 8. AI Agent Integration Patterns
- Claude Code / Codex integration via MCP
- GitHub Actions with AI review
- Automated agent creation and activation

---

## How to Use This Skill

### Loading the Skill
```bash
hermes -s salesforce-cli-expert
# or in chat:
/skill salesforce-cli-expert
```

### Common Workflows

#### Deploy Metadata to Org
```bash
dev project deploy start --target-org myOrg
```

#### Create Scratch Org for Testing
```bash
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias dev-org \
  --set-default
```

#### Deploy an Agentforce Agent
```bash
# Generate spec with LLM
echo '{"role": "Support", "company": "Corp"}' | sf agent generate agent-spec --full-interview

# Create authoring bundle
sf agent generate authoring-bundle --spec specs/agent.yaml --name Agent_Name

# Validate & publish
dev agent validate authoring-bundle --api-name Agent_Name
sf agent publish authoring-bundle --api-name Agent_Name --target-org devhub

# Activate
sf agent activate --api-name Agent_Name --version 1 --target-org devhub
```

#### Run Tests with Coverage
```bash
dev apex run test --result-format human --wait 10 --code-coverage
```

---

## Key Technical Concepts

### Agentforce Data Libraries (ADL)
Knowledge sources that ground agent responses:
- **SFDRIVE**: File upload with full Data Cloud pipeline provisioning
- **KNOWLEDGE**: Salesforce Knowledge articles indexing
- **RETRIEVER**: Existing Custom Retriever integration

Library ID format: 18-char Salesforce ID with prefix `1JD`

### Agent Script Language
The `.agent` file extension contains the domain-specific language that defines:
- Topics (what the agent can do)
- Actions (how it executes tasks)
- Routing logic (which topic/action to use)
- State management variables
- Context variable bindings ($Context.Name patterns)

### Authoring Bundles
Metadata type `AiAuthoringBundle` containing:
- Standard metadata XML file
- Agent Script file (.agent) — the agent blueprint

### Programmatic Preview Sessions
For CI/CD and automated testing:
```bash
sf agent preview start --authoring-bundle My_Agent_Bundle --simulate-actions
sf agent preview send --utterance "test message" --session-id <ID>
sf agent preview end --session-id <ID> --api-name My_Agent_Bucket
```

---

## Resources & References

| Resource | URL |
|----------|-----|
| Official CLI Page | https://developer.salesforce.com/tools/salesforcecli |
| Command Reference | https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/ |
| Setup Guide PDF | https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/sfdx_setup.pdf |
| GitHub (CLI) | https://github.com/forcedotcom/cli |
| Plugin Agent Repo | https://github.com/salesforcecli/plugin-agent |
| sf-skills Repository | https://github.com/forcedotcom/sf-skills |
| Agentscript | https://github.com/salesforce/agentscript |
| sf-pi (API) | https://github.com/salesforce/sf-pi |
| Agent Skills Spec | https://agentskills.io/ |

---

## Created Artifacts

### 1. Expert Skill Document
- **Location**: `~/AppData/Local/hermes/skills/development/salesforce-cli-expert/SKILL.md`
- **Size**: ~22KB comprehensive documentation
- **Content**: Complete reference covering all aspects of sf CLI and Agentforce integration

### 2. Research Documentation (Obsidian)
- **Location**: `C:\Users\madco\Documents\Obsidian\Salesforce CLI Research.md`  
- **Size**: ~9.5KB documentation
- **Content**: Research methodology, technical findings, architecture diagrams, and all key concepts

### 3. This README (Documentation)
- Captures the research process and how to use this skill for other agents

---

## Key Takeaways

1. **sf is the future** — sfdx commands are deprecated; new work should use `sf`-style commands
2. **Agentforce plugin is official** — Salesforce provides complete CLI interface via `@salesforce/plugin-agent`
3. **Data libraries ground agent responses** — SFDRIVE, KNOWLEDGE, and RETRIEVER source types provide knowledge sources
4. **Authoring bundles are the blueprint** — Agent Script files define agent behavior using a domain-specific language
5. **Programmatic preview sessions enable CI/CD** — Start/send/end sessions allow automated testing in pipelines
6. **sf-skills follows open specification** — Curated skills optimized for AI tools like Claude Code, Codex, Cursor
7. **JWT auth is recommended for CI/CD** — Service-to-service authentication without interactive login
8. **OIDC is the modern approach** — Native Salesforce OIDC support eliminates RSA key management
9. **Agent testing framework supports rich evaluation** — 8+ evaluator types including semantic similarity and LLM-based quality ratings
10. **Complete automation pipeline exists** — Generate spec → Create bundle → Validate → Publish → Activate agents programmatically

---

## For Other Agents

To use this knowledge:
1. Load the skill: `hermes -s salesforce-cli-expert` or `/skill salesforce-cli-expert`
2. Follow the command patterns — all examples use actual sf commands with correct flag syntax
3. Understand the architecture — Agentforce plugin provides complete AI agent lifecycle management
4. Implement CI/CD — Use documented GitHub Actions patterns for automated deployments
5. Deploy agents programmatically — Follow the automated pipeline pattern for agent creation and activation

---

## Version History
- **v1.0.0** (2026-07-23): Initial compilation from official sources
