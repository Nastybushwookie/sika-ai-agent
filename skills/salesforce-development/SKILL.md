---
name: salesforce-development
description: "Salesforce development patterns — scratch orgs, metadata API, source tracking, deployment strategies, LWC, Apex testing, and CI/CD workflows."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - salesforce
      - development
      - metadata-api
      - deployment
      - lwc
      - apex
---

# Salesforce Development Patterns

## Source-Driven Development

### Source Tracking (Default for Scratch Orgs)
```bash
# Push local changes to org
sf project push --target-org my-scratch

# Pull org changes to local source
sf project pull --target-org my-scratch

# Check source tracking status
sf project status --target-org my-scratch
```

### Metadata API Mode (Production/Sandboxes without Source Tracking)
```bash
# Deploy with manifest (no source tracking)
sf project deploy start \
  --target-org prod \
  --manifest config/package.xml \
  --test-level RunSpecifiedTests \
  --metadata ApexClass:MyController,ApexTrigger:MyTrigger

# Retrieve with manifest
sf project retrieve start \
  --target-org prod \
  --manifest config/package.xml \
  --output-dir retrieved
```

## Scratch Org Best Practices

### When to Use Scratch Orgs
- **Feature development**: Isolated, disposable environments
- **Testing**: CI/CD pipelines, automated testing
- **Demo/previews**: Short-lived orgs for client demos
- **Package development**: Namespace-enabled scratch orgs

### Scratch Org Definition (project-scratch-def.json)
```json
{
  "orgName": "My Company",
  "edition": "Enterprise",
  "features": [
    "EnableSetPasswordInApi",
    "PersonAccounts",
    "Communities",
    "LiveAgent",
    "Chatter"
  ],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1EncryptedStorage": true
    },
    "securitySettings": {
      "passwordPolicies": {
        "validPasswordExpirationInDays": 90,
        "complexPassword": true
      }
    },
    "communitiesSettings": {
      "enableNetworksEnabled": true
    }
  }
}
```

### Org Shapes (Emulate Production)
```bash
# List available org shapes
sf org shape list --json

# Create from org shape
sf org create scratch \
  --org-def "Enterprise Edition" \
  --alias shape-scratch \
  --duration-days 30

# Create from specific org shape file
sf org create scratch \
  --definition-file config/org-shape.json \
  --alias prod-emulate \
  --duration-days 30
```

## Metadata API Patterns

### package.xml Best Practices
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <!-- Specific metadata (preferred over wildcards) -->
  <types>
    <members>MyController</members>
    <members>MyControllerTest</members>
    <name>ApexClass</name>
  </types>
  
  <!-- All objects of a type -->
  <types>
    <members>*</members>
    <name>CustomObject</name>
  </types>
  
  <version>67.0</version>
</Package>
```

### Common Metadata Types
```xml
<!-- Apex -->
<ApexClass>, <ApexTrigger>, <ApexPage>, <ApexComponent>

<!-- LWC -->
<LightningComponentBundle>

<!-- Objects -->
<CustomObject>, <CustomField>, <CustomLabel>

<!-- Permissions -->
<Profile>, <PermissionSet>, <Role>, <SharingRule>

<!-- Flow/Automation -->
<Flow>, <ProcessDefinition>, <Workflow>, <QuickAction>

<!-- Experience -->
<ExperienceBundle>, <Network>, <Site>

<!-- Integration -->
<RemoteSiteSetting>, <IntegrationUserSession>, <ConnectedApp>
```

## Deployment Strategies

### Strategy 1: Source Push/Pull (Scratch Orgs Only)
```bash
# Best for: Daily development in scratch orgs
sf project push --target-org dev        # Push changes
sf project pull --target-org dev         # Pull changes
```

### Strategy 2: Manifest-Based Deploy (Production)
```bash
# Best for: Production deployments, sandboxes
sf project deploy start \
  --target-org prod \
  --manifest config/package.xml \
  --test-level RunSpecifiedTests \
  --test-level RunLocalTests \
  --wait 60 \
  --ignore-conflicts
```

### Strategy 3: Metadata Type Deploy
```bash
# Best for: Deploying specific types without manifest
sf project deploy start \
  --target-org prod \
  --metadata ApexClass:MyController,Flow:MyFlow \
  --test-level RunLocalTests
```

### Deployment Test Levels
| Test Level | Description | Use Case |
|------------|-------------|----------|
| `NoTestRun` | Skip tests (risky) | Non-critical metadata |
| `RunSpecifiedTests` | Run specific tests | Production deploys |
| `RunLocalTests` | Run all org tests | Sandboxes |
| `RunAllTests` | Run all org tests | Full regression |

## LWC Development

### LWC Project Structure
```
force-app/main/default/lwc/
├── myComponent/
│   ├── myComponent.html
│   ├── myComponent.js
│   ├── myComponent.js-meta.xml
│   └── __tests__/
│       └── myComponent.test.js
├── .eslintrc.json
└── lwc.config.json
```

### LWC Deployment
```bash
# Deploy LWC to org
sf project deploy start \
  --target-org dev \
  --source-dir force-app/main/default/lwc

# Retrieve LWC from org
sf project retrieve start \
  --target-org dev \
  --metadata LightningComponentBundle
```

## Apex Testing

### Test Best Practices
```bash
# Run all tests with coverage
sf apex test run \
  --target-org dev \
  --wait 30 \
  --code-coverage \
  --result-format json \
  --result-path test-results.json

# Run specific test classes
sf apex test run \
  --target-org dev \
  --test-level RunSpecifiedTests \
  --tests MyControllerTest,MyServiceTest \
  --wait 30

# Run tests with detailed output
sf apex test run \
  --target-org dev \
  --result-format dot \
  --progress \
  --wait 60
```

### Test Coverage Requirements
- **Org deployment**: 75% average coverage minimum
- **Production deployment**: 75% average, 100% for each class
- **Managed package**: 100% for all classes

## CI/CD Patterns

### GitHub Actions Example
```yaml
name: Salesforce Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Salesforce CLI
        run: npm install -g @salesforce/cli
      
      - name: Auth with Dev Hub
        run: sf auth sfdx-url login --sfdx-url ${{ secrets.SF_DEVHUB_URL }}
        
      - name: Create Scratch Org
        run: sf org create scratch --definition-file config/project-scratch-def.json --alias ci --duration-days 1
        
      - name: Deploy Metadata
        run: sf project deploy start --target-org ci --test-level RunLocalTests
        
      - name: Run Tests
        run: sf apex test run --target-org ci --wait 30 --code-coverage
        
      - name: Delete Scratch Org
        run: sf org delete scratch --target-org ci --no-prompt
```

## Common Pitfalls

### Source Tracking Issues
- **Not in scratch org**: Source tracking only works in scratch orgs
- **Metadata API mode**: Production/sandboxes use metadata API (no source tracking)
- **Conflicts**: Use `--ignore-conflicts` flag when deploying to non-scratch orgs

### Deploy Failures
- **Test coverage**: Ensure 75%+ coverage before production deploy
- **Apex class size**: Keep classes under 1MB
- **API version**: Use latest API version (67.0 as of Summer '26)
- **Missing dependencies**: Ensure all referenced metadata types are included

### Scratch Org Limits
- **Max duration**: 30 days (extendable)
- **Max per org**: Depends on license
- **Namespace**: Required for package development
- **Features**: Limited by edition and available features

## References
- Metadata API: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_quickstart.htm
- Scratch Orgs: https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_scratch_orgs.htm
- LWC Development: https://developer.salesforce.com/docs/component-library/documentation/en/lwc
- Apex Testing: https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing.htm
