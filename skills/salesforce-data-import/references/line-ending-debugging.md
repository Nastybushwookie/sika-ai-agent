# Salesforce Bulk API 2.0 Line Ending Troubleshooting

## The Problem

When importing CSV files via `sf data import bulk`, you may encounter:

```
ClientInputError : LineEnding is invalid on user data. Current LineEnding setting is CRLF
```

This error means the CSV file's line endings don't match what Salesforce expects.

## Root Cause

Salesforce Bulk API 2.0 defaults to LF (Unix/Linux) line endings. If your CSV was created on Windows, it likely has CRLF (Windows) line endings. The API detects this mismatch and rejects the file.

## Diagnosis

### Check current line endings

```bash
# Show line endings (cat -A displays special chars)
cat -A your-file.csv | head -3

# LF endings: $ at end of line (no ^M)
Name,Industry,Phone,Website,BillingState,BillingCountry$
Acme Corp,Technology,415-555-0101,https://acme.demo,California,United States$

# CRLF endings: ^M$ at end of line (^M = carriage return)
Name,Industry,Phone,Website,BillingState,BillingCountry^M$
Acme Corp,Technology,415-555-0101,https://acme.demo,California,United States^M$
```

### Check file type

```bash
file your-file.csv
# CSV ASCII text → LF endings
# CSV ASCII text with CRLF line terminators → CRLF endings
```

## Fixes

### Convert LF to CRLF (if org expects CRLF)

```bash
sed -i 's/$/\r/' your-file.csv
```

### Convert CRLF to LF (if org expects LF — the default)

```bash
sed -i 's/\r$//' your-file.csv
```

### Verify the fix

```bash
cat -A your-file.csv | head -3
# Should show $ at end of lines (no ^M) for LF
```

## Prevention

### Always check before importing

```bash
# Quick check: does the file have CRLF?
grep -cP '\r$' your-file.csv
# If count > 0, file has CRLF endings
```

### When creating CSV files in bash

```bash
# Create CSV with LF endings (safe default)
printf "Name,Industry\nAcme,Technology\n" > file.csv
```

### When creating CSV files on Windows

- Use a text editor that lets you choose line endings (VS Code, Notepad++)
- Set line ending to LF in the editor
- Or convert after creation: `sed -i 's/\r$//' file.csv`

## Common Scenarios

### Scenario 1: Fresh CSV created on Windows, importing to Salesforce
**Problem:** CRLF endings rejected by Bulk API
**Fix:** `sed -i 's/\r$//' file.csv` (convert to LF)

### Scenario 2: CSV created on Linux, failing with CRLF error
**Problem:** Rare, but can happen with certain file transfers
**Fix:** `sed -i 's/$/\r/' file.csv` (convert to CRLF)

### Scenario 3: Mixed line endings in CSV
**Problem:** Some lines have LF, others have CRLF
**Fix:**
```bash
# First convert all to LF
sed -i 's/\r$//' file.csv
# Then verify uniform
cat -A file.csv | head -3
```

## Related Skills

- `salesforce-cli-expert` — General Salesforce CLI reference
- `salesforce-data-import` — Bulk data import patterns and workflows
