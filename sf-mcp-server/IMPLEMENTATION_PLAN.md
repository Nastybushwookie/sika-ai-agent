# Custom Salesforce MCP Server — Implementation Plan

## Research Summary

### What We Found
1. **Official Salesforce DX MCP Server** (`github.com/salesforcecli/mcp`) — TypeScript/Node.js, 445+ stars, 252 releases, actively maintained. Wraps `sf` CLI commands as MCP tools.
2. **Python SF MCP Server** (`salesforce-mcp-server` on PyPI) — Published Jan 2026, provides multi-user OAuth 2.0 PKCE auth.
3. **Salesforce Hosted MCP Servers** — GA April 2026, cloud-hosted for Agentforce (not local).
4. **MCP Official SDKs** — TypeScript SDK (Tier 1) and Python SDK (Tier 1) from `modelcontextprotocol`.
5. **sf CLI** is installed (v2.144.6) and has a Developer Edition org connected.

### Decision: Build from scratch using Python MCP SDK
- We have Python 3.11 available
- Python SDK is Tier 1 (feature-complete)
- Easier to customize for our specific needs
- Can leverage `sf` CLI via subprocess for DX operations
- Can add REST API calls for operations the CLI doesn't expose

---

## Architecture

```
sf-mcp-server/
├── pyproject.toml          # Project config, dependencies
├── src/
│   └── sf_mcp/
│       ├── __init__.py     # Entry point: main()
│       ├── server.py       # MCP server setup, tool registration
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── soql.py           # SOQL query tools
│       │   ├── records.py        # CRUD operations (create, update, delete, upsert)
│       │   ├── metadata.py       # Metadata operations (describe, retrieve)
│       │   ├── org.py            # Org management (list, open, create scratch)
│       │   ├── deploy.py         # Deploy/retrieve via sf CLI
│       │   └── auth.py           # Auth state management
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── manager.py        # SF CLI auth wrapper
│       │   └── credentials.py    # Token storage (encrypted)
│       └── utils/
│           ├── __init__.py
│           ├── sf_wrapper.py     # Subprocess wrapper for `sf` CLI
│           └── salesforce_api.py # Direct REST API calls
├── tests/
│   ├── test_tools.py
│   └── test_auth.py
├── README.md
└── .env.example
```

---

## Tool Design

### Tier 1: Core SOQL & Record Operations (Must Have)
| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `sf_soql_query` | Execute SOQL query, return records | query (str), max_results (int, default 200) |
| `sf_record_get` | Get a single record by ID | sobject_type (str), record_id (str) |
| `sf_record_create` | Create a new record | sobject_type (str), fields (json) |
| `sf_record_update` | Update an existing record | sobject_type (str), record_id (str), fields (json) |
| `sf_record_delete` | Delete a record | sobject_type (str), record_id (str) |
| `sf_sobject_describe` | Describe an object's metadata | sobject_type (str) |

### Tier 2: Metadata & DX Operations
| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `sf_list_objects` | List all objects (standard + custom) | (none) |
| `sf_describe_layout` | Describe a page layout | sobject_type (str), layout_name (str) |
| `sf_org_list` | List authenticated orgs | (none) |
| `sf_org_open` | Open default org in browser | (none) |
| `sf_org_create_scratch` | Create a scratch org | definition_file, alias, duration_days |
| `sf_project_deploy` | Deploy metadata to org | source_dir, target_org |
| `sf_project_retrieve` | Retrieve metadata from org | target_org, output_dir, component_types |

### Tier 3: Agentforce Operations
| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `sf_agent_list` | List Agentforce agents | (none) |
| `sf_agent_create` | Create an agent | name, api_name, spec_file, target_org |
| `sf_agent_activate` | Activate an agent | api_name, version, target_org |
| `sf_agent_deactivate` | Deactivate an agent | api_name, target_org |
| `sf_adl_list` | List Data Libraries | (none) |
| `sf_adl_create` | Create a Data Library | name, developer_name, source_type, target_org |
| `sf_adl_upload` | Upload file to Data Library | library_id, file_path, target_org |

### Tier 4: User Management & Security
| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `sf_user_list` | List users | (none) |
| `sf_profile_list` | List profiles | (none) |
| `sf_permission_set_list` | List permission sets | (none) |

---

## Implementation Phases

### Phase 1: Foundation (Day 1)
- [ ] Initialize Python project with pyproject.toml
- [ ] Install `mcp`, `simple-salesforce` (for REST API)
- [ ] Create MCP server skeleton with `mcp.server`
- [ ] Implement `sf_soql_query` tool (most critical first)
- [ ] Test locally with MCP Inspector

### Phase 2: Core CRUD (Day 2)
- [ ] Implement record CRUD tools
- [ ] Implement object describe
- [ ] Implement auth manager (reuse sf CLI auth)
- [ ] Test with real Salesforce org

### Phase 3: DX Operations (Day 3)
- [ ] Implement sf CLI wrapper (subprocess)
- [ ] Implement metadata tools
- [ ] Implement org management tools
- [ ] Implement deploy/retrieve tools

### Phase 4: Agentforce + Polish (Day 4-5)
- [ ] Implement agent management tools
- [ ] Implement Data Library tools
- [ ] Add comprehensive error handling
- [ ] Write README with usage examples
- [ ] Configure in Hermes Agent config.yaml

---

## Technical Details

### Authentication Strategy
- **Primary**: Reuse existing sf CLI auth tokens (stored in `~/.sfdx/`)
- The `sf` CLI handles OAuth token refresh automatically
- Our server calls `sf` commands via subprocess, inheriting sf's auth state
- No need for separate OAuth flow — leverage what's already configured

### REST API Fallback
- For operations `sf` CLI doesn't expose well, use `simple-salesforce` library
- `simple-salesforce` reads auth from `~/.sfdx/` or environment variables
- Provides direct REST API access for SOQL, CRUD, metadata describe

### Key Dependencies
```
mcp>=1.0.0          # Official MCP Python SDK
simple-salesforce>=1.1.0  # Salesforce REST API client
cryptography>=42.0  # Token encryption (optional)
```

### Testing Strategy
1. **Local unit tests** — mock sf CLI responses
2. **MCP Inspector** — `npx @modelcontextprotocol/inspector` to test tool discovery
3. **Live org tests** — use Developer Edition org for real SOQL/CRUD tests
4. **Hermes integration** — configure in config.yaml, verify tools appear

---

## Hermes Agent Configuration (Target)
```yaml
mcp_servers:
  sf:
    command: "uvx"
    args: ["-p", "sf-mcp-server"]
    # OR if installed locally:
    # command: "python"
    # args: ["-m", "sf_mcp"]
    timeout: 180
    connect_timeout: 60
```

---

## Risk & Mitigation
| Risk | Mitigation |
|------|------------|
| sf CLI auth tokens expire | simple-salesforce fallback with same tokens |
| subprocess timeouts | configurable timeout, async subprocess calls |
| SOQL governor limits | warn in tool description, respect 50K limit |
| Python `mcp` SDK version issues | Pin to latest stable, test with MCP Inspector |
