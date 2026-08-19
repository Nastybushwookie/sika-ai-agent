@echo off
REM Fix Salesforce MCP org alias in Hermes config.yaml
REM Usage: run this from any directory

set "CONFIG_FILE=%LOCALAPPDATA%\hermes\config.yaml"

if not exist "%CONFIG_FILE%" (
    echo ERROR: config.yaml not found at %CONFIG_FILE%
    exit /b 1
)

echo Fixing Salesforce MCP org alias...
echo Current value: DEFAULT_TARGET_ORG
echo New value: williampullins@gmail.com

python -c "
import yaml, sys

config_file = r'%LOCALAPPDATA%\hermes\config.yaml'

with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Fix the org alias
sf_server = config.get('mcp_servers', {}).get('sf', {})
args = sf_server.get('args', [])

for i, arg in enumerate(args):
    if arg == 'DEFAULT_TARGET_ORG':
        args[i] = 'williampullins@gmail.com'
        print(f'Replaced arg at index {i}: {arg} -> williampullins@gmail.com')
        break

sf_server['args'] = args
config['mcp_servers']['sf'] = sf_server

with open(config_file, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f'Wrote config back to {config_file}')
print('Done. Restart Hermes to apply changes.')
"

pause
