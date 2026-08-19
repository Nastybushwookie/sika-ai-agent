#!/usr/bin/env python3
"""
Fix Salesforce MCP org alias in Hermes config.yaml.
Replaces DEFAULT_TARGET_ORG placeholder with the actual org username.

Usage:
  python scripts/fix-sf-mcp-org-alias.py              # interactive prompt
  python scripts/fix-sf-mcp-org-alias.py orgalias     # non-interactive

After running, restart Hermes to reload the MCP server with the correct org.
"""
import yaml
import os
import sys

CONFIG_FILE = os.path.expanduser(os.path.join(
    os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
    'hermes', 'config.yaml'
))

if not os.path.exists(CONFIG_FILE):
    CONFIG_FILE = os.path.expanduser('~/.hermes/config.yaml')

if not os.path.exists(CONFIG_FILE):
    print(f"ERROR: config.yaml not found")
    sys.exit(1)

print(f"Config file: {CONFIG_FILE}")
print(f"Fixing Salesforce MCP org alias...")
print(f"  Old value: DEFAULT_TARGET_ORG")

# Get target org: CLI arg or interactive prompt
if len(sys.argv) > 1:
    target_org = sys.argv[1]
else:
    print(f"Current orgs (from 'sf org list'):")
    # Try to list orgs via sf CLI
    import subprocess
    try:
        result = subprocess.run(
            ['sf', 'org', 'list', '--json'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            for rec in data.get('result', {}).get('records', []):
                username = rec.get('Username', '')
                alias = rec.get('Alias', '')
                status = rec.get('Status', '')
                print(f"  - {username} (alias: {alias}) [{status}]")
    except Exception:
        pass
    target_org = input("Enter the org alias/username to use: ").strip()

if not target_org:
    print("ERROR: No org specified")
    sys.exit(1)

print(f"  New value: {target_org}")

with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

sf_server = config.get('mcp_servers', {}).get('sf', {})
args = sf_server.get('args', [])

replaced = False
for i, arg in enumerate(args):
    if arg == 'DEFAULT_TARGET_ORG':
        args[i] = target_org
        print(f"  Replaced arg at index {i}")
        replaced = True
        break

if not replaced:
    print("  WARNING: DEFAULT_TARGET_ORG not found in args")
    print(f"  Current args: {args}")
    sys.exit(1)

sf_server['args'] = args
config['mcp_servers']['sf'] = sf_server

with open(CONFIG_FILE, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"  Wrote config back to {CONFIG_FILE}")
print("Done. Restart Hermes to apply changes.")
