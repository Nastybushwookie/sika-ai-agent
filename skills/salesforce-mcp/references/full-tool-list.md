# Salesforce DX MCP Server — Full Tool List

Research compiled from github.com/salesforcecli/mcp README (v0.30.15).

## Core Toolset (always enabled)
- `get_username` — Determines appropriate username/alias for operations
- `resume_tool_operation` — Resumes long-running operations

## Data Toolset
- `run_soql_query` — Runs SOQL query against a Salesforce org

## Metadata Toolset
- `deploy_metadata` — Deploys metadata from DX project to org
- `retrieve_metadata` — Retrieves metadata from org to DX project

## Orgs Toolset
- `list_all_orgs` (GA) — List all configured Salesforce orgs with connection status
- `create_scratch_org` (NON-GA) — Create a scratch org
- `delete_org` (NON-GA) — Delete a locally-authorized scratch org or sandbox
- `open_org` (NON-GA) — Open an org in a browser
- `create_org_snapshot` (NON-GA) — Create a scratch org snapshot

## Users Toolset
- `assign_permission_set` (GA) — Assign a permission set to a user

## Testing Toolset
- `run_apex_test` (GA) — Executes Apex tests in your org
- `run_agent_test` (GA) — Executes agent tests in your org

## LWC Experts Toolset (30+ tools)
### Component Development
- `create_lwc_component_from_prd` — Creates complete LWC components from PRD specs
- `create_lwc_jest_tests` — Generates Jest test suites for LWC
- `review_lwc_jest_tests` — Reviews and validates Jest tests

### Development Guidelines
- `create_lightning_type` — Guidance for Custom Lightning Types
- `guide_design_general` — SLDS guidelines and best practices
- `guide_component_accessibility` — Accessibility guidelines
- `guide_lwc_best_practices` — LWC coding standards
- `guide_lwc_development` — LWC workflow and implementation
- `guide_lwc_rtl_support` — RTL internationalization support
- `guide_lws_security` — Security analysis per product guidelines
- `lwc-doc-error` — Retrieves LWC error message info
- `reference_lwc_compilation_error` — References LWC compilation errors
- `guide_lbc_usage` — Index of Lightning Base Components
- `explore_lbc_components` — LBC API documentation

### LDS (Lightning Data Service)
- `create_lds_graphql_mutation_query` — GraphQL mutation guidance
- `create_lds_graphql_read_query` — GraphQL read queries
- `explore_lds_uiapi` — UI API capabilities
- `fetch_lds_graphql_schema` — GraphQL schema structure
- `guide_lds_data_consistency` — Data consistency patterns
- `guide_lds_development` — LDS development guidelines
- `guide_lds_graphql` — GraphQL usage patterns
- `guide_lds_referential_integrity` — Referential integrity patterns
- `orchestrate_lds_data_requirements` — LDS data requirements analysis
- `test_lds_graphql_query` — Tests GraphQL query against org

### Migration & Workflow
- `guide_figma_to_lwc_conversion` — Figma to LWC specs
- `guide_lo_migration` — Lightning Out migration
- `run_lwc_accessibility_jest_tests` — Accessibility testing
- `verify_aura_migration_completeness` — Aura-to-LWC checklist
- `orchestrate_lwc_component_creation` — Component creation workflow
- `orchestrate_lwc_component_optimization` — Performance optimization
- `orchestrate_lwc_component_testing` — Testing workflow

## Code Analysis Toolset
- `run_code_analyzer` — Static analysis (best practices, security, performance)
- `describe_code_analyzer_rule` — Gets rule description
- `list_code_analyzer_rules` — Selects rules by criteria
- `query_code_analyzer_results` — Queries results JSON file

## Aura Experts Toolset
- `create_aura_blueprint_draft` — Aura component migration PRD
- `enhance_aura_blueprint_draft` — Enhances draft with expert analysis
- `orchestrate_aura_migration` — Complete Aura-to-LWC workflow
- `transition_prd_to_lwc` — LWC implementation guidance

## DevOps Center Toolset
- `list_devops_center_projects` — List projects in org
- `list_devops_center_work_items` — List work items for project
- `create_devops_center_work_item` — Create new work item
- `update_devops_center_work_item_status` — Set status to In Progress/Ready
- `promote_devops_center_work_item` — Promote to next pipeline stage
- `checkout_devops_center_work_item` — Checkout feature branch
- `commit_devops_center_work_item` — Commit changes and register SHA
- `create_devops_center_pull_request` — Create PR to feature branch
- `detect_devops_center_merge_conflict` — Detect merge conflicts
- `resolve_devops_center_merge_conflict` — Apply conflict resolution
- `resolve_devops_center_deployment_failure` — Diagnose deployment failures

## Experts Validation Toolset
- `validate_and_optimize` — Returns validation runbook (accessibility, security, best practices)
- `score_issues` — Computes readiness score (0-100) and quality grade

## Scale Products Toolset
- `scan_apex_class_for_antipatterns` — Analyzes Apex for performance antipatterns

## Enrichment Toolset
- `enrich_metadata` (NON-GA) — Enrich metadata from org in DX project

## Mobile Toolsets
- 20+ LWC mobile-specific tools (barcode, biometrics, calendar, location, NFC, payments, etc.)
- `get_mobile_lwc_offline_analysis` — Analyzes components for mobile offline issues
- `get_mobile_lwc_offline_guidance` — Structured offline code review instructions