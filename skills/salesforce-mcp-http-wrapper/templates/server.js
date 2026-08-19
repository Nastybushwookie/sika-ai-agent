/**
 * SF MCP HTTP Wrapper (Simple Version)
 * Uses Salesforce CLI (sf) directly to expose Salesforce operations as HTTP endpoints
 * This avoids the complexity of MCP stdio communication
 */

const express = require('express');
const cors = require('cors');
const { execFile } = require('child_process');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3001;
const SF_CLI = 'C:\\Users\\madco\\AppData\\Roaming\\npm\\sf.cmd';

// Helper to run sf CLI commands
function runSfCommand(args, timeout = 30000) {
    return new Promise((resolve, reject) => {
        const proc = execFile(SF_CLI, args, { timeout, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
            if (error) {
                resolve({ error: stderr || error.message });
                return;
            }
            try {
                resolve(JSON.parse(stdout));
            } catch {
                resolve({ raw: stdout.trim() });
            }
        });
        
        proc.on('error', (err) => {
            resolve({ error: `Failed to run sf CLI: ${err.message}` });
        });
    });
}

// Tool definitions for Vapi
const SALESFORCE_TOOLS = [
    {
        name: 'sf_list_accounts',
        description: 'List Salesforce accounts',
        parameters: {
            limit: { type: 'number', description: 'Max records to return' }
        }
    },
    {
        name: 'sf_get_account',
        description: 'Get a Salesforce account by ID',
        parameters: {
            account_id: { type: 'string', description: 'Account ID' }
        }
    },
    {
        name: 'sf_create_lead',
        description: 'Create a Salesforce lead',
        parameters: {
            first_name: { type: 'string' },
            last_name: { type: 'string' },
            email: { type: 'string' },
            company: { type: 'string' },
            phone: { type: 'string' }
        }
    },
    {
        name: 'sf_list_contacts',
        description: 'List Salesforce contacts',
        parameters: {
            limit: { type: 'number' }
        }
    },
    {
        name: 'sf_create_contact',
        description: 'Create a Salesforce contact',
        parameters: {
            first_name: { type: 'string' },
            last_name: { type: 'string' },
            email: { type: 'string' },
            phone: { type: 'string' },
            account_id: { type: 'string' }
        }
    },
    {
        name: 'sf_list_opportunities',
        description: 'List Salesforce opportunities',
        parameters: {
            account_id: { type: 'string' },
            limit: { type: 'number' }
        }
    },
    {
        name: 'sf_create_opportunity',
        description: 'Create a Salesforce opportunity',
        parameters: {
            name: { type: 'string' },
            account_id: { type: 'string' },
            amount: { type: 'number' },
            close_date: { type: 'string' },
            stage: { type: 'string' }
        }
    },
    {
        name: 'sf_create_case',
        description: 'Create a Salesforce case',
        parameters: {
            subject: { type: 'string' },
            description: { type: 'string' },
            contact_id: { type: 'string' },
            priority: { type: 'string' }
        }
    },
    {
        name: 'sf_get_user_info',
        description: 'Get current Salesforce user info',
        parameters: {}
    },
    {
        name: 'sf_list_users',
        description: 'List Salesforce users',
        parameters: {
            limit: { type: 'number' }
        }
    }
];

// Tool implementations
async function executeTool(toolName, params) {
    switch (toolName) {
        case 'sf_list_accounts': {
            const limit = params.limit || 10;
            const result = await runSfCommand(['data', 'query', '--query', 
                `SELECT Id, Name, Phone, Industry FROM Account LIMIT ${limit}`, '--result-format', 'json']);
            return result;
        }
        
        case 'sf_get_account': {
            const accountId = params.account_id;
            if (!accountId) return { error: 'account_id is required' };
            const result = await runSfCommand(['data', 'query', '--query',
                `SELECT Id, Name, Phone, Industry FROM Account WHERE Id = '${accountId}' LIMIT 1`, '--result-format', 'json']);
            return result;
        }
        
        case 'sf_create_lead': {
            const { first_name, last_name, email, company, phone } = params;
            if (!first_name || !last_name) return { error: 'first_name and last_name are required' };
            const result = await runSfCommand(['data', 'upsert', '--entity', 'Lead', '--key-field', 'Email',
                '--value', JSON.stringify({
                    FirstName: first_name,
                    LastName: last_name,
                    Email: email,
                    Company: company,
                    Phone: phone
                }), '--result-format', 'json']);
            return result;
        }
        
        case 'sf_list_contacts': {
            const limit = params.limit || 10;
            const result = await runSfCommand(['data', 'query', '--query',
                `SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT ${limit}`, '--result-format', 'json']);
            return result;
        }
        
        case 'sf_create_contact': {
            const { first_name, last_name, email, phone, account_id } = params;
            if (!first_name || !last_name) return { error: 'first_name and last_name are required' };
            const result = await runSfCommand(['data', 'upsert', '--entity', 'Contact', '--key-field', 'Email',
                '--value', JSON.stringify({
                    FirstName: first_name,
                    LastName: last_name,
                    Email: email,
                    Phone: phone,
                    AccountId: account_id
                }), '--result-format', 'json']);
            return result;
        }
        
        case 'sf_list_opportunities': {
            const limit = params.limit || 10;
            const accountIdFilter = params.account_id ? ` WHERE AccountId = '${params.account_id}'` : '';
            const result = await runSfCommand(['data', 'query', '--query',
                `SELECT Id, Name, AccountId, Amount, CloseDate, StageName FROM Opportunity${accountIdFilter} LIMIT ${limit}`, '--result-format', 'json']);
            return result;
        }
        
        case 'sf_create_opportunity': {
            const { name, account_id, amount, close_date, stage } = params;
            if (!name) return { error: 'name is required' };
            const result = await runSfCommand(['data', 'upsert', '--entity', 'Opportunity', '--key-field', 'Name',
                '--value', JSON.stringify({
                    Name: name,
                    AccountId: account_id,
                    Amount: amount,
                    CloseDate: close_date,
                    StageName: stage || 'Prospecting'
                }), '--result-format', 'json']);
            return result;
        }
        
        case 'sf_create_case': {
            const { subject, description, contact_id, priority } = params;
            if (!subject) return { error: 'subject is required' };
            const result = await runSfCommand(['data', 'upsert', '--entity', 'Case', '--key-field', 'CaseNumber',
                '--value', JSON.stringify({
                    Subject: subject,
                    Description: description,
                    ContactId: contact_id,
                    Priority: priority || 'Medium'
                }), '--result-format', 'json']);
            return result;
        }
        
        case 'sf_get_user_info': {
            const result = await runSfCommand(['config', 'get', 'target-org']);
            return result;
        }
        
        case 'sf_list_users': {
            const limit = params.limit || 10;
            const result = await runSfCommand(['data', 'query', '--query',
                `SELECT Id, Username, FirstName, LastName, Email FROM User LIMIT ${limit}`, '--result-format', 'json']);
            return result;
        }
        
        default:
            return { error: `Unknown tool: ${toolName}` };
    }
}

// API Routes

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        sfCliAvailable: true
    });
});

// List available tools
app.get('/tools', (req, res) => {
    res.json({ tools: SALESFORCE_TOOLS });
});

// Execute a tool (generic endpoint)
app.post('/tools/call', async (req, res) => {
    try {
        const { tool, args } = req.body;
        
        if (!tool) {
            return res.status(400).json({ error: 'Tool name is required' });
        }
        
        const result = await executeTool(tool, args || {});
        res.json({ result });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Vapi-compatible tool endpoints
app.post('/vapi/tools', async (req, res) => {
    try {
        const { tool_name, parameters } = req.body;
        
        if (!tool_name) {
            return res.status(400).json({ error: 'tool_name is required' });
        }
        
        const result = await executeTool(tool_name, parameters || {});
        
        // Format result for Vapi
        res.json({
            toolCallId: req.body.toolCallId || uuidv4(),
            result: result
        });
    } catch (error) {
        res.status(500).json({
            toolCallId: req.body.toolCallId || uuidv4(),
            result: { error: error.message }
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`SF MCP HTTP Wrapper running on http://localhost:${PORT}`);
    console.log(`Available tools: ${SALESFORCE_TOOLS.map(t => t.name).join(', ')}`);
});
