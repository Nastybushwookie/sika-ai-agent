# Creating Users in Regular (Non-Scratch) Salesforce Orgs

## The Problem

`sf org user create` **only works for scratch orgs**. It returns an error for regular orgs:

```
» Warning: org user create is not a sf command.
```

## The Solution: `sf data create record`

Use `sf data create record --sobject User` with all required fields.

### Step 1: Get the ProfileId

```bash
sf data query --query "SELECT Id, Name FROM Profile WHERE Name='Standard User' LIMIT 1"
```

For System Administrator:
```bash
sf data query --query "SELECT Id, Name FROM Profile WHERE Name='System Administrator' LIMIT 1"
```

### Step 2: Create the User

```bash
sf data create record \
  --sobject User \
  --values "FirstName='Agent' LastName='Wookiee' \
  Username='agentbushwookiee2@example.com' \
  Email='agentbushwookiee@gmail.com' \
  Alias='ABWookie' \
  ProfileId='00ehm000000UXXPAA4' \
  IsActive=true \
  TimeZoneSidKey='America/New_York' \
  LocaleSidKey='en_US' \
  LanguageLocaleKey='en_US' \
  EmailEncodingKey='UTF-8'"
```

### Required Fields (all must be provided)

| Field | Required | Notes |
|-------|----------|-------|
| `FirstName` | Yes | |
| `LastName` | Yes | |
| `Username` | Yes | Must be unique, valid email format. Use `@example.com` for test orgs. |
| `Email` | Yes | Can be different from Username |
| `Alias` | Yes | **Max 8 characters** — not 15! |
| `ProfileId` | Yes | Get from `sf data query` |
| `IsActive` | Yes | `true` or `false` |
| `TimeZoneSidKey` | Yes | e.g., `America/New_York`, `UTC` |
| `LocaleSidKey` | Yes | Usually `en_US` |
| `LanguageLocaleKey` | Yes | Usually `en_US` |
| `EmailEncodingKey` | Yes | **Always required** — use `UTF-8` |

### Username Format

Salesforce usernames must be valid email format. For test orgs, use `@example.com`:

```
agentbushwookiee2@example.com
```

The actual email goes in the `Email` field:

```
agentbushwookiee@gmail.com
```

### First Login

New users created via API **cannot set a password directly**. They must:
1. Go to `https://<instance>.lightning.force.com/lightning/page/home`
2. Click "Forgot your password?"
3. Reset via email sent to the `Email` field

Or from the admin org, use the "Reset Password" button in Setup → Users.
