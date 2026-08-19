#!/usr/bin/env python3
"""
Fix Salesforce MCP org alias in Hermes config.yaml.
Replaces DEFAULT_TARGET_ORG with your actual org username.
"""
import yaml
import os
import sys

CONFIG_FILE = os.path.expanduser(os.path.join(
    os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
    'hermes', 'config.yaml'
))

if not os.path.exists(CONFIG_FILE):
    # Try ~/.hermes/config.yaml as fallback
    CONFIG_FILE = os.path.expanduser('~/.hermes/config.yaml')

if not os.path.exists(CONFIG_FILE):
    print(f"ERROR: config.yaml not found")
    print(f"Searched:")
    print(f"  {os.environ.get('LOCALAPPDATA', 'N/A')}\\hermes\\config.yaml")
    print(f"  ~/.hermes/config.yaml")
    sys.exit(1)

print(f"Config file: {CONFIG_FILE}")
print(f"Fixing Salesforce MCP org alias...")
print(f"  Old value: DEFAULT_TARGET_ORG")
print(f"  New value: williampullins@gmail.com")

with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

# Fix the org alias
sf_server = config.get('mcp_servers', {}).get('sf', {})
args = sf_server.get('args', [])

replaced = False
for i, arg in enumerate(args):
    if arg == 'DEFAULT_TARGET_ORG':
        args[i] = 'williampullins@gmail.com'
        print(f"  Replaced arg at index {i}: {arg} -> williampullins@gmail.com")
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
