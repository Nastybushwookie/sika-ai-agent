---
name: salesforce-cli
description: "Salesforce CLI (sf) command reference — auth, scratch orgs, metadata deploy/retrieve, SOQL, org management. Covers sf v2 commands, deprecated sfdx migration, and common workflows."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - salesforce
      - sf-cli
      - salesforce-dx
      - cli
---

# Salesforce CLI (sf) Command Reference

## Overview
The `sf` CLI (v2.144.6+) is the unified Salesforce CLI replacing the deprecated `sfdx` CLI. All `sfdx force:*` commands are deprecated — use `sf` equivalents.

## Installation
```bash
# Install via npm (requires Node.js 20+)
npm install -g @salesforce/cli

# Verify installation
sf --version

# Update to latest
sf update
```

## Authentication Commands

### Login to Org
```bash
# Login to production/DE org (web-based OAuth)
sf org login web --alias sika-dev

# Login with username and password (for automation)
sf org login username --username USERNAME --password PASSWORD --callback-url http://localhost:1717/

# Login with Dev Hub (required for scratch orgs)
sf org login web --devhub --alias devhub

# Login with existing access token
sf auth sfdx-url login --sfdx-url "https://login.salesforce.com?id=XXX&access_token=YYY"
```

### Auth Management
```bash
# List all authenticated orgs
sf org list

# Show org details
sf org display --json

# Show auth info for specific org
sf org auth show --target-org williampullins@gmail.com

# Check access token
sf org auth show-access-token --target-org williampullins@gmail.com

# Set default org
sf org set default --target-org williampullins@gmail.com

# Unauthorize an org
sf auth revoke -t williampullins@gmail.com

# Refresh token
sf auth refresh -t williampullins@gmail.com
```

### Auth Token for API Usage
```bash
# Get access token programmatically
sf auth display --json --target-org williampullins@gmail.com
# Parse from JSON output: result.accessToken and result.instanceUrl

# Use in curl/API calls
curl -s https://orgfarm-4344f57ecf.my.salesforce.com/services/data/v67.0/chatter/users/me \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Using Existing Access Token (no full auth flow)
```bash
# When you have a token but don't want full CLI auth
# Set environment variables:
export SF_TARGET_ORG_INSTANCE_URL="https://orgfarm-4344f57ecf.my.salesforce.com"
export SF_TARGET_ORG_ACCESS_TOKEN="ACCESS_TOKEN_HERE"

# Then use sf commands with --target-org
sf org display --target-org williampullins@gmail.com
```

## Scratch Org Management

### Create Scratch Org
```bash
# Basic scratch org (5 days)
sf org create scratch --definition-file config/project-scratch-def.json --alias my-scratch --duration-days 5

# With features
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias dev-scratch \
  --duration-days 30 \
  --set-default

# From org shape (emulate production org)
sf org create scratch \
  --org-def "Enterprise Edition" \
  --alias shape-scratch \
  --duration-days 7

# With specific features
sf org create scratch \
  --definition-file config/project-scratch-def.json \
  --alias test-scratch \
  --duration-days 5 \
  --features "EnableSetPasswordInApi" \
  --flags "DeployStatus=Completed"
```

### scratch-def.json Template
```json
{
  "orgName": "My Company",
  "edition": "Enterprise",
  "features": ["EnableSetPasswordInApi", "PersonAccounts", "Communities"],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1EncryptedStorage": true
    },
    "securitySettings": {
      "passwordPolicies": {
        "validPasswordExpirationInDays": 90
      }
    }
  }
}
```

### Manage Scratch Orgs
```bash
# List all scratch orgs
sf org list --type scratch

# Open scratch org in browser
sf org open --target-org my-scratch

# Delete scratch org
sf org delete scratch --target-org my-scratch --no-prompt

# Get scratch org URL
sf org display --json --target-org my-scratch | grep instanceUrl
```

## Metadata Operations

### Deploy Metadata
```bash
# Deploy from source directory
sf project deploy start \
  --target-org williampullins@gmail.com \
  --source-dir force-app \
  --test-level RunLocalTests

# Deploy with manifest
sf project deploy start \
  --target-org williampullins@gmail.com \
  --manifest config/package.xml \
  --test-level RunLocalTests \
  --wait 30

# Deploy with specific metadata types
sf project deploy start \
  --target-org williampullins@gmail.com \
  --metadata ApexClass,CustomObject \
  --test-level RunLocalTests

# Deploy with ignore conflicts
sf project deploy start \
  --target-org williampullins@gmail.com \
  --source-dir force-app \
  --ignore-conflicts

# Check deploy status
sf project deploy status --json
```

### Retrieve Metadata
```bash
# Retrieve all metadata from org
sf project retrieve start \
  --target-org williampullins@gmail.com \
  --source-dir force-app

# Retrieve with manifest
sf project retrieve start \
  --target-org williampullins@gmail.com \
  --manifest config/package.xml \
  --output-dir force-app

# Retrieve specific metadata types
sf project retrieve start \
  --target-org williampullins@gmail.com \
  --metadata ApexClass:MyController,CustomObject:MyObject__c

# Retrieve to specific directory
sf project retrieve start \
  --target-org williampullins@gmail.com \
  --metadata ApexClass \
  --output-dir retrieved-metadata
```

### package.xml Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <types>
    <members>MyController</members>
    <name>ApexClass</name>
  </types>
  <types>
    <members>MyObject__c</members>
    <name>CustomObject</name>
  </types>
  <version>67.0</version>
</Package>
```

## Data Operations

### SOQL Queries
```bash
# Run SOQL query
sf query --query "SELECT Id, Name, Industry FROM Account LIMIT 10" --target-org williampullins@gmail.com

# Output as JSON
sf query --query "SELECT Id, Name FROM Account LIMIT 5" --target-org williampullins@gmail.com --json

# Save results to file
sf query --query "SELECT Id, Name FROM Account LIMIT 100" --target-org williampullins@gmail.com > accounts.json
```

### Data Import/Export
```bash
# Export data to CSV
sf data export query --query "SELECT Id, Name FROM Account" --target-org williampullins@gmail.com --result-format csv --result-path accounts.csv

# Import from CSV
sf data import start --target-org williampullins@gmail.com --object-type Account --source-path accounts.csv
```

## Org Management

### Org Operations
```bash
# Open org in browser
sf org open --target-org williampullins@gmail.com

# Open Lightning page
sf org open --target-org williampullins@gmail.com --path "/lightning/o/Account/home"

# Get org info
sf org display --target-org williampullins@gmail.com --json

# Create sandbox
sf org create sandbox \
  --target-dev-hub devhub \
  --name dev-sandbox \
  --wait 60

# Delete sandbox
sf org delete sandbox --target-org dev-sandbox --no-prompt
```

### Org Snapshots
```bash
# Create org snapshot
sf org create snapshot --target-org williampullins@gmail.com --alias my-snapshot

# Restore from snapshot
sf org restore snapshot --target-org williampullins@gmail.com --snapshot-alias my-snapshot
```

## Project Commands

### Initialize Project
```bash
# Create new DX project
sf project init --alias my-project --default-dev-hub devhub

# Create new project with specific template
sf project new --name my-app --template "core"

# Add metadata to project
sf project generate --target-org williampullins@gmail.com
```

### Project Structure
```
my-project/
├── config/
│   ├── project-scratch-def.json
│   └── package.xml
├── force-app/
│   ├── main/
│   │   ├── default/
│   │   │   ├── classes/
│   │   │   ├── lwc/
│   │   │   └── objects/
│   │   └── primary/
│   └── secondary/
├── sfdx-project.json
└── .forceignore
```

## Testing

### Run Tests
```bash
# Run all tests
sf apex test run --target-org williampullins@gmail.com --wait 30

# Run specific tests
sf apex test run \
  --target-org williampullins@gmail.com \
  --test-level RunSpecifiedTests \
  --tests MyControllerTest

# Run with result format
sf apex test run --target-org williampullins@gmail.com --result-format dot --progress

# Run Apex tests (alternative)
sf apex test run --target-org williampullins@gmail.com --wait 60 --code-coverage
```

## Common Workflows

### Standard Development Workflow
```bash
# 1. Login to Dev Hub
sf org login web --devhub --alias devhub

# 2. Create scratch org
sf org create scratch --definition-file config/project-scratch-def.json --alias dev --duration-days 5

# 3. Open scratch org
sf org open --target-org dev

# 4. Make changes, then deploy
sf project deploy start --target-org dev --test-level RunLocalTests

# 5. Run tests
sf apex test run --target-org dev --wait 30

# 6. Retrieve changes
sf project retrieve start --target-org dev --source-dir force-app

# 7. Delete scratch org when done
sf org delete scratch --target-org dev --no-prompt
```

### Deploy to Production
```bash
# 1. Login to production
sf org login web --alias prod

# 2. Deploy with manifest
sf project deploy start \
  --target-org prod \
  --manifest config/package.xml \
  --test-level RunSpecifiedTests \
  --test-level RunLocalTests \
  --wait 60 \
  --ignore-conflicts

# 3. Check deployment status
sf project deploy status --json
```

## Windows-Specific Notes

### PATH Configuration
```bash
# The sf CLI is installed at:
# C:\Users\madco\AppData\Local\hermes\node\node_modules\@salesforce\cli

# If sf not found, use full path:
/c/Users/madco/AppData/Local/hermes/node/node_modules/@salesforce/cli/bin/sf.cmd --version
```

### Common Issues
- **sf not found in bash**: Use `sf.cmd` or full path on Windows
- **Node.js version**: Requires Node 20+. Check with `node --version`
- **Line endings**: Use `git config core.autocrlf input` for Salesforce projects
- **File paths**: Use forward slashes in package.xml and config files

## Deprecated sfdx → sf Migration

| Deprecated sfdx Command | New sf Command |
|------------------------|----------------|
| `sfdx force:auth:web:login` | `sf org login web` |
| `sfdx force:org:list` | `sf org list` |
| `sfdx force:org:create` | `sf org create scratch` |
| `sfdx force:mdapi:deploy` | `sf project deploy start` |
| `sfdx force:mdapi:retrieve` | `sf project retrieve start` |
| `sfdx force:data:soql:query` | `sf query` |
| `sfdx force:apex:test:run` | `sf apex test run` |
| `sfdx force:source:push` | `sf project push` |
| `sfdx force:source:pull` | `sf project pull` |

## Quick Reference

### Most Common Commands
```bash
sf org list                                    # List orgs
sf org login web --alias my-org                # Login
sf org open --target-org my-org                # Open org
sf query --query "SOQL" --target-org my-org    # Run SOQL
sf project deploy start --target-org my-org    # Deploy
sf project retrieve start --target-org my-org  # Retrieve
sf apex test run --target-org my-org           # Run tests
sf org create scratch --alias my-scratch       # Create scratch org
sf org delete scratch --target-org my-scratch  # Delete scratch org
```

## References
- Official CLI Reference: https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/
- Salesforce DX Developer Guide: https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/
- GitHub: https://github.com/forcedotcom/cli
- Release Notes: https://github.com/forcedotcom/cli/releases
