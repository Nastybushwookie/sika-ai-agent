# Salesforce Skills Reference

This directory contains 14 Salesforce-related Hermes Agent skills copied from the Hermes Agent skill library.

## Skills List

| Skill | Description | Files |
|-------|-------------|-------|
| `salesforce-cli` | Salesforce CLI (sf) command reference — auth, scratch orgs, metadata deploy/retrieve, SOQL, org management | 1 file |
| `salesforce-cli-expert` | Salesforce CLI expert reference with advanced workflows and troubleshooting | 2 files |
| `salesforce-development` | Scratch orgs, metadata API, source tracking, deployment strategies, LWC, Apex testing | 1 file |
| `salesforce-auth` | Salesforce authentication patterns — OAuth flows, token management, refresh strategies | 1 file |
| `salesforce-mcp` | Salesforce MCP server patterns — use the official @salesforce/mcp-server | 4 files |
| `salesforce-mcp-server` | Set up, configure, and troubleshoot the Salesforce DX MCP server | 10 files |
| `salesforce-mcp-http-wrapper` | Expose stdio-based Salesforce MCP as HTTP API for Vapi.ai integration | 2 files |
| `salesforce-mcp-integration` | Configure and use the Salesforce MCP integration with Vapi.ai | 1 file |
| `salesforce-integration` | Use when building Salesforce integrations for AI agents | 2 files |
| `salesforce-integration-patterns` | Review FastAPI/Python projects with Salesforce integration | 2 files |
| `salesforce-data-import` | Bulk data import patterns for Salesforce — CSV creation, deployment, validation | 2 files |
| `salesforce-demo-prep` | Populate Salesforce orgs for manager demos — check org capacity, create records | 1 file |
| `salesforce-expert` | Deep expertise in Salesforce platform architecture, editing, and best practices | 1 file |
| `salesforce-vapi-integration` | Use when building Salesforce + Vapi.ai integrations locally | 2 files |

## Usage

These skills are loaded automatically by Hermes Agent when working with Salesforce tasks. They provide:

- CLI command references for the `sf` CLI
- OAuth2 authentication workflows
- MCP server setup and configuration
- Vapi.ai integration patterns
- Data import/export procedures
- Demo preparation checklists
- Troubleshooting guides

## Source

Copied from Hermes Agent skill library on 2026-08-19. Original skill library at `~/.hermes/skills/`.
