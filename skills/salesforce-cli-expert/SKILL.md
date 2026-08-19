---
name: salesforce-cli-expert
description: "Complete expert reference for Salesforce CLI (sf) including installation, authentication, org management, Agentforce plugin commands, CI/CD patterns, and AI agent integration. Covers official Salesforce repositories: salesforcecli/plugin-agent, forcedotcom/sf-skills, and all sf command categories."
version: 1.0.0
author: Hermes Agent + Research compiled from official sources
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, cli, sf, sfdx, agentforce, devops, ci-cd, automation, ai-agents, plugin-agent, sf-skills]
---

# Salesforce CLI (sf) — Complete Expert Reference

## Overview & Version History

Salesforce CLI (`sf`) is the supported command-line interface for Salesforce DX development. In 2026+, all new work should use `sf`-style commands; older `sfdx`-style commands are deprecated.

**Key versions:**
- **sf (v2)** — Current, recommended
- **sfdx (v7)** — Deprecated but still functional during transition period

```bash
# Verify installation
sf --version  # Expected: @salesforce/cli/x.x.x win32-x64 node-v22.xx.x
sf commands   # Lists all available commands
```

## Installation Methods

### npm (Cross-platform, recommended)
```bash
npm install -g @salesforce/cli
sf --version  # Verify installation
```

### Homebrew (macOS/Linux)
```bash
# macOS
brew tap salesforce/tap && brew install sf

# Linux
brew install sf
```

### Windows Download
- x64: https://developer.salesforce.com/tools/salesforcecli
- ARM64: Available for Apple Silicon / ARM Windows devices

### Verification & Basic Commands
```bash
sf --version           # Check version
sf commands            # List all available commands
sf help                # General help
sf COMMAND --help      # Help for specific command
```

## Project Structure (.sfdx-project.json)

The project file defines the Salesforce DX project structure:

```json
{
  "packageDirectories": [
    {
      "path": "force-app",
      "default": true
    },
    {
      "path": "force-app/main/default"
    }
  ],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "62.0"
}
```

### Project Creation & Structure
```bash
# Create new DX project
sf project generate --name my-project --template standard

# Directory structure created:
force-app/main/default/classes/          # Apex classes
force-app/main/default/objects/           # Custom objects  
force-app/main/default/layouts/           # Page layouts
force-app/main/default/pages/             # Visualforce pages
force-app/main/default/triggers/          # Triggers
force-app/main/default/flows/             # Flow metadata
config/project-scratch-def.json           # Scratch org definition
```

## Authentication Methods (5 Types)

### 1. Web Login (Interactive, for developers)
```bash
sf org login web
# Opens browser → Salesforce login page → OAuth callback
# Sets the logged-in org as default
```

### 2. Username/Password Login (CI/CD automation)
```bash
sf org login username \
  --username user@example.com \
  --password MyPassword123! \
  --set-default
```
- Requires: User credentials + security token (if IP restrictions exist)
- Use environment variables for secrets:
```bash
export SF_LOGIN_USERNAME=user@example.com
export SF_LOGIN_PASSWORD=MyPassword123!
sf org login username
```

### 3. JWT Bearer Flow (Service-to-service, recommended for CI/CD)
```bash
# Generate RSA key pair locally
genjwt --keyfile jwt.key

# Create connected app in Salesforce DevHub with JWT callback configured
# Upload public key to org: Setup → Apps → Connected Apps → New Connected App

# Authenticate using private key
sf org login jwt \
  --client-id 04580y4051234051 \
  --jwt-key-file /path/to/jwt.key \
  --username admin@example.com \
  --instance-url https://test.salesforce.com \
  --set-default
```
- **Best for CI/CD pipelines** — no interactive login needed
- Requires: Connected App with JWT callback configured, private key on build server

### 4. Access Token (Machine-to-machine)
```bash
sf org login access-token \
  --instance-url https://test.salesforce.com \
  --access-token $(salesforce_access_token) \
  --set-default
```
- Use when you have an OAuth token directly
- Common in GitHub Actions with OIDC-based authentication

### 5. IP Allowlist (No auth command needed)
```bash
# If your org has "Login IP Ranges" set, add CI server IPs there
# Then use username/password login without security token
```

## Org Management

### Scratch Orgs (Temporary Dev Environments)
Scratch orgs are ephemeral, configurable Salesforce environments for development and testing.

```bash
# Create scratch org from definition file
sf project generate --name config/project-scratch-def.json
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias dev-org \
  --set-default \
  --duration-days 30
```

### Scratch Org Definition (project-scratch-def.json)
```json
{
  "orgName": "My Company",
  "edition": "Developer",  // Developer, Professional, Enterprise, Unlimited
  "features": [
    "Communities",
    "Chatter",
    "EinsteinAnalytics"
  ],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1DesktopEnabled": true
    },
    "mobileSettings": {
      "enableS1EncryptedStoragePref2": false
    }
  }
}
```

Common `edition` values:
- **Developer**: Full access, no cost (good for dev/test)
- **Professional**: Limited customization
- **Enterprise**: Full customization + API access
- **Unlimited**: Maximum flexibility

### DevHub Org (Required for Scratch Orgs)
You need a DevHub org to create scratch orgs:
```bash
# Enable DevHub in an Enterprise/Unlimited org
sf org login web --alias devhub
sf org enable devhub
```

### Common Org Commands
```bash
sf org list                          # List all orgs
sf org open                          # Open default org in browser
sf org open -o my-org                # Open specific org
sf org delete scratch -o my-org      # Delete scratch org
sf org set-default my-org            # Set default org
```

## Project Workflows

### Initialize & Configure
```bash
# Create new DX project
dx init my-project --template standard

# Add source directory structure
force-app/main/default/classes/          # Apex classes
force-app/main/default/objects/           # Custom objects
force-app/main/default/layouts/           # Page layouts
force-app/main/default/pages/             # Visualforce pages
force-app/main/default/triggers/          # Triggers
force-app/main/default/flows/             # Flow metadata
```

### Deploy & Retrieve Metadata
```bash
# Deploy all source to default org
sf project deploy start

# Deploy specific directory or file
deploy --source-dir force-app/main/default/classes/MyClass.cls

# Retrieve entire org metadata to local project
retrieve --target-org MyOrg --output-dir retrieved-meta/

# Retrieve specific component types
retrieve --target-org MyOrg \
  --component-type ApexClass,CustomObject,Flow
```

### Source Push/Pull (Synchronize with Org)
```bash
# Push local changes to org
dev push

# Pull changes from org to project
dev pull

# Sync all source (push + pull in one command)
sync
```

## Testing & Execution

### Run Apex Tests
```bash
sf apex run test --result-format human --wait 10

# Run tests with coverage report
apex test run --code-coverage --result-format json \
  --output-dir test-results/

# Run specific test class
test run -c MyClassTest --class-name MyClassTest
```

### Query Records (SOQL)
```bash
# Execute SOQL query from file
sf data query --query-file queries/my-query.soql

# Interactive query console
sf org explore
```

## Agentforce & AI Agent Integration

### sf plugin-agent Commands (Official Salesforce Plugin)
The `plugin-agent` package adds commands for interacting with Agentforce AI agents.

**Installation:**
```bash
sf plugins install @salesforce/plugin-agent@latest
```

#### Data Library Management (ADL - Agentforce Data Libraries)
Data libraries are knowledge sources that ground agent responses:

```bash
# Create SFDRIVE library (file upload)
sf agent adl create \
  --target-org myOrg \
  --name "My Docs" \
  --developer-name My_Docs \
  --source-type sfdrive

# Create KNOWLEDGE library (Salesforce Knowledge articles)
sf agent adl create \
  --target-org myOrg \
  --name "KB Library" \
  --developer-name KB_Library \
  --source-type knowledge \
  --primary-index-field1 Title \
  --primary-index-field2 Summary

# Create RETRIEVER library (existing Custom Retriever)
sf agent adl create \
  --target-org myOrg \
  --name "Existing Retriever" \
  --developer-name Existing_Retriever \
  --source-type retriever \
  --retriever-id 0ppXX0000000001
```

#### File Management for Data Libraries
```bash
# Upload files to SFDRIVE library (triggers indexing)
sf agent adl upload \
  --library-id 1JDSG000007IbWX4A0 \
  --file ./docs/guide.pdf \
  --target-org myOrg

# Add files to existing library (appends, triggers re-indexing)
sf agent adl file add \
  -i 1JDSG000007IbWX4A0 \
  --path ./docs/new-guide.pdf \
  --target-org myOrg

# List files in library
sf agent adl file list \
  -i 1JDSG000007IbWX4A0 \
  --target-org myOrg

# Delete file from library
sf agent adl file delete \
  -i 1JDSG000007IbWX4A0 \
  --file-id a1B2C3D4E5F6G7H8I9 \
  --target-org myOrg
```

#### Agent Lifecycle Management
```bash
# Create agent from spec file
sf agent create \
  --name "Resort Manager" \
  --api-name Resort_Manager \
  --spec specs/resortManagerAgent.yaml \
  --target-org my-org

# Preview agent (interactive conversation)
sf agent preview --target-org my-dev-org

# Preview with live actions
dev preview --use-live-actions --apex-debug

# Activate published agent
sf agent activate --api-name Resort_Manager --version 2 --target-org my-org

# Deactivate agent
sf agent deactivate --api-name Resort_Manager --target-org my-org
```

#### Agent Script & Authoring Bundles (Agentforce DX)
Authoring bundles contain the Agent Script file — the blueprint for agents:

```bash
# Generate agent spec (YAML with AI-generated topics)
sf agent generate agent-spec \
  --type customer \
  --role "Field customer complaints and manage employee schedules" \
  --company-name "Coral Cloud Resorts" \
  --company-description "Provide customers with exceptional destination activities"

# Generate authoring bundle from spec
sf agent generate authoring-bundle \
  --spec specs/agentSpec.yaml \
  --name "My Authoring Bundle"

# Validate Agent Script compiles
sf agent validate authoring-bundle \
  --api-name MyAuthoringBundle \
  --target-org my-dev-org

# Publish to org (creates Bot, BotVersion metadata)
sf agent publish authoring-bundle \
  --api-name MyAuthoringBundle \
  --target-org my-dev-org
```

#### Programmatic Agent Preview Sessions
For CI/CD and automated testing:

```bash
# Start programmatic session
sf agent preview start \
  --authoring-bundle My_Agent_Bundle \
  --target-org my-dev-org \
  --simulate-actions

# Send utterance to session
sf agent preview send \
  --utterance "What can you help me with?" \
  --api-name My_Published_Agent \
  --session-id <SESSION_ID>

# List sessions
sf agent preview sessions

# End session
sf agent preview end \
  --session-id <SESSION_ID> \
  --api-name My_Published_Agent
```

#### Agent Testing Framework
```bash
# Generate test spec (YAML with test cases)
sf agent generate test-spec \
  --output-file specs/Resort_Manager-testSpec.yaml \
  --test-runner agentforce-studio

# Create test in org
sf agent test create \
  --spec specs/Resort_Manager-testSpec.yaml \
  --api-name Resort_Manager_Test \
  --force-overwrite \
  --target-org my-org

# Run tests
sf agent test run \
  --api-name Resort_Manager_Test \
  --wait 10 \
  --result-format junit \
  --target-org my-org

# Get results (supports human, json, junit, tap formats)
sf agent test results \
  --job-id 4KBfake0000003F4AQ \
  --output-dir ./test-results \
  --result-format json
```

#### Agent Tracing & Debugging
```bash
# List trace files from preview sessions
sf agent trace list

# Read session traces (summary, detail, raw formats)
sf agent trace read \
  --session-id <SESSION_ID> \
  --format detail \
  --dimension actions  # actions|grounding|routing|errors

# Delete old traces
dev trace delete --older-than 7d --no-prompt
```

#### MCP Server Management (Agentforce)
Register external MCP servers for agent use:

```bash
# Create MCP server in API Catalog
sf agent mcp create \
  --name myServer \
  --server-url https://mcp.example.com \
  --target-org myOrg

# List registered MCP servers
dev mcp list --status ACTIVE

# Fetch live assets from MCP server
sf agent mcp fetch \
  --mcp-server-id 0XSxx0000000001 \
  --target-org myOrg

# List assets (tools, prompts, resources)
sf agent mcp asset list \
  --mcp-server-id 0XSxx0000000001 \
  --target-org myOrg

# Update MCP server
dev mcp update \
  --mcp-server-id 0XSxx0000000001 \
  --label "Orders MCP" \
  --description "Order tooling"
```

## sf-skills (Curated Skills Collection)

Salesforce maintains a curated collection of skills optimized for Agentforce:

**Repository:** https://github.com/forcedotcom/sf-skills

### Key Skill Categories
- **platform-apex-generate** — Production-grade Apex class generation with mandatory test generation, code analyzer validation, and deployment checks
- **automation-flow-generate** — Flow metadata generation via strict 3-step MCP pipeline (fetchGroundedObjectMetadata → flowElementSelection → flowElementGeneration)
- **platform-custom-object-generate** — Custom object creation with proper metadata structure
- **automation-flow-design-patterns** — Flow design patterns and best practices
- **lwc-component-generate** — Lightning Web Component generation

### Installing sf-skills for AI Tools
```bash
# For OpenCode, Claude Code, Codex, Cursor
npx skills add forcedotcom/sf-skills
```

### Agentforce Skills Architecture
Each skill follows the open [Agent Skills specification](https://agentskills.io/):
- `SKILL.md` (required): Instructions and YAML front matter
- `scripts/` (optional): Executable scripts (Python, Bash, JavaScript)
- `references/` (optional): Extra reference documentation  
- `assets/` (optional): Templates, schemas, lookup data

## CI/CD Integration with GitHub Actions

### Basic Workflow Pattern
```yaml
name: Salesforce CI/CD
defaults:
  run:
    working-directory: ./force-app

jobs:
  # Install Salesforce CLI in the job runner
  - name: Setup sf CLI
    uses: forcedotcom/setup-salesforce-cli@v2
    with:
      sf_cli_version: 'latest'

  # Authenticate using JWT (recommended for CI/CD)
  - name: Login to Salesforce Org via JWT Flow
    run: |
      sf org login jwt \
        --client-id ${{ secrets.SF_CLIENT_ID }} \
        --jwt-key-file ${{ secrets.SF_JWT_KEY_FILE }} \
        --username ${{ secrets.SF_USERNAME }} \
        --set-default

  # Deploy metadata to target org
  - name: Deploy to Target Org
    run: sf project deploy start

  # Run Apex Tests with Code Coverage
  - name: Run Apex Tests
    run: sf apex test run --result-format human --wait 10 --code-coverage
```

### GitHub Actions with OIDC (Modern, No Keys)
```yaml
# Uses Salesforce's native OIDC support — no JWT keys needed!
name: Deploy to Production
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup sf CLI
        uses: forcedotcom/setup-salesforce-cli@v2
      
      - name: Login to Salesforce Org via OAuth Web Flow
        uses: forceddotcom/salesforcedx-commands-prebuilt@latest
        with:
          verbose: 'true'
        env:
          SF_USERNAME: ${{ secrets.SF_PROD_USERNAME }}
          SF_PASSWORD: ${{ secrets.SF_PROD_PASSWORD }}
      
      - name: Deploy to Production  
        run: sf project deploy start --target-org prod-org
```

### Environment Variables for CI/CD
```yaml
# Common env vars used in GitHub Actions:
SF_LOGIN_USERNAME       # Username for org login
SF_LOGIN_PASSWORD       # Password (or use secrets)
SF_CLIENT_ID           # Connected app consumer key  
SF_JWT_KEY_FILE        # Path to private RSA key file
SF_INSTANCE_URL        # Salesforce instance URL
```

## Using sf with AI Coding Agents

### Pattern 1: Claude Code / Codex Integration via MCP
```json
// Add to your Claude Code or Hermes Agent config:
{
  "mcpServers": {
    "salesforce": {
      "command": "sf",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Pattern 2: GitHub Actions with AI Review
```yaml
# Use sf in CI to deploy, then AI agent reviews code changes
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy & Test
        uses: forcedotcom/setup-salesforce-cli@v2
      
      - name: Deploy Metadata
        run: sf project deploy start
      
      - name: AI Review of Changes (using LLM)
        run: |
          # Get diff and send to AI for review
          git diff --staged > changes.diff
          # ... process with your LLM agent
```

### Pattern 3: Automated Scratch Org Management
```bash
#!/bin/bash
# Create scratch org, push code, run tests, report results
set -e

ORG_ALIAS="ci-test-$(date +%Y%m%d%H%M)"
sf project deploy start --target-org $ORG_ALIAS
sf apex test run --result-format human --wait 10
echo "Tests passed! Cleaning up scratch org..."
sf org delete scratch --alias $ORG_ALIAS --no-prompt
```

### Pattern 4: Agentforce Plugin with AI Automation
```bash
#!/bin/bash
# Automated agent deployment workflow
set -e

# Generate spec with LLM
echo '{"role": "Customer Support", "company": "Acme Corp"}' | sf agent generate agent-spec --full-interview --output-file specs/autoAgent.yaml

# Create authoring bundle
sf agent generate authoring-bundle --spec specs/autoAgent.yaml --name Auto_Agent

# Publish to org
sf agent publish authoring-bundle --api-name Auto_Agent --target-org devhub

# Activate agent
sf agent activate --api-name Auto_Agent --version 1 --target-org devhub
```

## Common Troubleshooting

### Auth Issues
```bash
# Check current auth state
dev auth list

# Re-authenticate a specific org
auth web login -o MyOrgAlias

# Clear all cached credentials (dangerous — deletes local tokens)
auth revoke --all
```

### Deployment Errors
```bash
# Get detailed deployment status
sf project deploy history

# Check recent deployments
dev deploy list --json
```

### Version Conflicts
```bash
# Ensure you're using sf (not deprecated sfdx)
sf version
# Should show: @salesforce/cli/x.x.x ... node-vxx.xx.x
```

## Key Resources & References

| Resource | URL |
|----------|-----|
| Official CLI | https://developer.salesforce.com/tools/salesforcecli |
| Command Reference | https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/ |
| Setup Guide PDF | https://resources.docs.salesforce.com/latest/latest/en-us/sfdc/pdf/sfdx_setup.pdf |
| GitHub (CLI) | https://github.com/forcedotcom/cli |
| Plugin Agent | https://github.com/salesforcecli/plugin-agent |
| sf-skills | https://github.com/forcedotcom/sf-skills |
| Agentscript | https://github.com/salesforce/agentscript |
| sf-pi (API) | https://github.com/salesforce/sf-pi |
| Agent Skills Spec | https://agentskills.io/ |

## Architecture Overview

### Metadata Types Used by sf Commands
- **AiAuthoringBundle** — Agent blueprint (contains Agent Script file)
- **Bot** / **BotVersion** — Published agent definitions  
- **GenAiPlannerBundle** / **GenAiX** — Agent configuration metadata
- **AiEvaluationDefinition** — Legacy test runner metadata
- **AiTestingDefinition** — Agentforce Studio (NGT) test metadata
- **Data Cloud Assets** (DLO, DMO, SearchIndex, Retriever) — Data library infrastructure

### Agentforce Plugin Command Categories
1. **Agent Lifecycle**: `activate`, `deactivate`, `create`, `generate`
2. **Authoring Bundles**: `publish authoring-bundle`, `validate authoring-bundle`  
3. **Data Libraries (ADL)**: `adl create/delete/list/get/update/upload/status`
4. **File Management**: `adl file add/delete/list`
5. **Preview Sessions**: `preview start/send/end/sessions`, trace reading
6. **Testing**: `test create/run/resume/results/run-eval/generate test-spec`
7. **MCP Servers**: `mcp create/list/get/update/delete/fetch/asset list/replace`
8. **Templates**: `generate template` (for managed packages)
9. **Tracing**: `trace delete/list/read` for debugging agent behavior

### Agent Script Language
The `.agent` file extension contains the Agent Script — a domain-specific language that defines:
- Topics (what the agent can do)  
- Actions (how it executes tasks)
- Routing logic (which topic/action to use)
- State management variables
- Context variable bindings ($Context.Name patterns)

## Integration with Hermes Agent

### Using sf Commands in Hermes
```bash
# Run sf commands via terminal tool
terminal(command="sf org list")

# Deploy metadata
terminal(command="sf project deploy start --target-org myOrg")

# Create scratch org
dev org create scratch --definition-file config/project-scratch-def.json --alias dev1
```

### Automated Agentforce Workflows with Hermes
```bash
#!/bin/bash
# Complete agent deployment workflow using sf CLI
set -e

# 1. Generate agent spec based on requirements
sf agent generate agent-spec \
  --type customer \
  --role "Handle customer inquiries about orders" \
  --company-name "My Company" \
  --output-file specs/customerAgent.yaml

# 2. Create authoring bundle from spec
dev agent generate authoring-bundle \
  --spec specs/customerAgent.yaml \
  --name Customer_Agent

# 3. Validate the Agent Script compiles
dev agent validate authoring-bundle --api-name Customer_Agent --target-org devhub

# 4. Publish to org (creates Bot, BotVersion metadata)
sf agent publish authoring-bundle \
  --api-name Customer_Agent \
  --target-org devhub

# 5. Activate the published agent
dev agent activate --api-name Customer_Agent --version 1 --target-org devhub
```
