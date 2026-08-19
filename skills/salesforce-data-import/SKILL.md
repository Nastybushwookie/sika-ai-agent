---
name: salesforce-data-import
description: "Bulk data import patterns for Salesforce — CSV creation, line ending fixes, bulk API 2.0 workflows, and Developer Edition limits. Covers sf data import bulk, line ending troubleshooting, and field requirements."
version: 1.0.0
author: Hermes Agent + Research compiled from official sources
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, data-import, bulk-api, csv, developer-edition, sf-cli]
---

# Salesforce Bulk Data Import

## Overview

Bulk data import uses Salesforce Bulk API 2.0 via `sf data import bulk`. This is the recommended method for importing large datasets (thousands of records) into Salesforce objects.

## Critical Line Ending Rule

**THE #1 CAUSE OF BULK IMPORT FAILURES: Line endings must match the declared format.**

The Bulk API 2.0 defaults to LF line endings. If your CSV has CRLF (Windows-style) line endings, the import will fail with:

```
ClientInputError : LineEnding is invalid on user data. Current LineEnding setting is CRLF
```

### Fixing Line Endings

**Convert LF to CRLF (for orgs expecting CRLF):**
```bash
sed -i 's/$/\r/' your-file.csv
```

**Convert CRLF to LF (for orgs expecting LF — the default):**
```bash
sed -i 's/\r$//' your-file.csv
```

**Verify line endings:**
```bash
cat -A your-file.csv | head -3
# LF endings show: $ at end of line
# CRLF endings show: ^M$ at end of line
```

## Bulk Import Workflow

### Step 1: Create CSV File

Headers must match Salesforce field API names exactly. Required fields must be included.

```csv
Name,Industry,Phone,Website,BillingState,BillingCountry
Acme Corp,Technology,415-555-0101,https://acme.demo,California,United States
```

### Step 2: Convert Line Endings

```bash
# For CRLF (Windows)
sed -i 's/$/\r/' file.csv

# For LF (Unix/Linux default)
sed -i 's/\r$//' file.csv
```

### Step 3: Create Bulk Import Job

```bash
sf data import bulk --file file.csv --sobject Account
# Returns: Job ID and URL to resume
```

### Step 4: Resume the Job

```bash
sf data import resume --job-id 750hm000001XXXXXXX
# Returns: Processed/Successful/Failed record counts
```

### Step 5: Check Results

```bash
# Get job details
sf data bulk results --job-id 750hm000001XXXXXXX

# View failed records
cat 750hm000001XXXXXXX-failed-records.csv

# View successful records
cat 750hm000001XXXXXXX-success-records.csv
```

## Common Field Requirements

### Account Object
- **Name** (required)
- **BillingState** requires **BillingCountry** to be specified first
- **Phone**, **Website**, **Industry** (optional)

### Contact Object
- **FirstName** (required)
- **LastName** (required)
- **Email** (optional)
- **AccountId** (required for relationship)

### Opportunity Object
- **Name** (required)
- **AccountId** (required)
- **StageName** (required — valid values: Prospecting, Qualification, Needs Analysis, Value Proposition, Proposal, Negotiation, Closed Won, Closed Lost)
- **Amount** (optional)
- **CloseDate** (required — format: YYYY-MM-DD)

### Case Object
- **Subject** (required)
- **Description** (required)
- **Status** (required — valid values: New, Working, Escalated, Closed, Inactive)
- **Priority** (required — valid values: Low, Medium, High, Critical)
- **Origin** (required — valid values: Email, Phone, Web, Chat, Other)
- **Type** (optional)
- **AccountId** (optional)
- **ContactId** (optional)

## Developer Edition Limits

| Limit | Value |
|-------|-------|
| Custom Objects | 10 max |
| Data Storage | 5 MB |
| File Storage | 20 MB |
| API Calls | Limited per day |
| Quote Object | NOT available in Developer Edition |
| Order Object | Limited availability |

**Note:** Quote and Order objects may not be available in all Developer Edition orgs. Use standard objects (Account, Contact, Opportunity, Case) for demo data.

## Troubleshooting

### Error: "LineEnding is invalid on user data"
**Cause:** CSV line endings don't match the org's expected format.
**Fix:** Convert line endings using `sed` (see above).

### Error: "Field name not found : X"
**Cause:** CSV header uses wrong field name or field doesn't exist on the object.
**Fix:** Check Salesforce field API names. Use `sf data query --query "SELECT Id FROM Account LIMIT 1"` to see available fields.

### Error: "FIELD_INTEGRITY_EXCEPTION: A country/territory must be specified"
**Cause:** BillingState specified without BillingCountry.
**Fix:** Add BillingCountry column to CSV with valid country values (e.g., "United States").

### Error: "InvalidBatch : Unable to find object: Quote"
**Cause:** Quote object not available in this org (Developer Edition limitation).
**Fix:** Use Opportunity or Case instead for demo data.

### Error: "Nonexistent flag: --id"
**Cause:** Wrong command syntax for sf CLI version.
**Fix:** Use `sf data delete record --sobject Account --id <id>` (not `--id` flag).

## Reference Files

See `references/` directory for:
- `salesforce-developer-edition-limits.md` — Detailed limits and guidelines
- `bulk-import-field-mapping.md` — Object field reference mappings
- `line-ending-debugging.md` — Detailed CRLF/LF troubleshooting guide

## Templates

See `templates/` directory for:
- `account-import-csv.csv` — Account import template
- `contact-import-csv.csv` — Contact import template
- `opportunity-import-csv.csv` — Opportunity import template

## Scripts

See `scripts/` directory for:
- `fix-crlf-line-endings.sh` — Script to convert line endings
- `verify-bulk-import.sh` — Script to verify import results
