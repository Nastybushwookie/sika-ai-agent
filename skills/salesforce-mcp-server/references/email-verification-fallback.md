# Email Verification Without Himalaya CLI

## Problem
Himalaya CLI may not be available on the target machine. It's a Rust binary distributed via GitHub releases, not on npm.

### Why himalaya failed to install
- `npm install -g @pimalaya/himalaya` → 404 (wrong package name)
- `winget install pimalaya.himalaya` → not found
- `choco install himalaya` → not available
- `scoop install himalaya` → not available
- GitHub releases: `curl -L` downloads work but files don't persist in /tmp on this Windows setup (bash MSYS temp path)

## Fallback: Raw Node.js TLS IMAP

The SF MCP HTTP wrapper already has nodemailer installed for **sending**. For **reading**, use raw Node.js TLS:

```javascript
// test-imaps.js — verify IMAP connection and credentials
const tls = require('tls');
const socket = tls.connect({ host: 'imap.gmail.com', port: 993, rejectUnauthorized: false });
let step = 0;
socket.on('data', (data) => {
  const str = data.toString();
  console.log('>>> ' + str.trim().replace(/\r\n/g, '\n'));
  if (str.includes('* OK') && step === 0) { step = 1; send('a001 LOGIN <user> <pass>'); }
  else if (str.startsWith('a001 OK') && step === 1) { step = 2; send('a002 EXAMINE INBOX'); }
  else if (str.startsWith('a002 OK') && step === 2) { step = 3; send('a003 SEARCH ALL'); }
  else if (str.startsWith('* SEARCH') && step === 3) {
    const ids = str.replace('* SEARCH', '').trim().split(/\s+/).filter(Boolean);
    console.log(`Found ${ids.length} messages`);
    send('a004 LOGOUT');
  }
});
function send(cmd) { console.log('<<< ' + cmd); socket.write(cmd + '\r\n'); }
socket.on('error', (err) => { console.error('Error:', err.message); process.exit(1); });
```

### Reading actual messages — multi-line response handling

IMAP responses come in chunks:
- `* 32 FETCH (BODY[HEADER.FIELDS (FROM SUBJECT DATE)] {162}` — the `{162}` means 162 bytes follow
- The actual header data arrives in a separate line
- The `a004 OK Success` line signals completion

**Key pitfall:** The `data` event may split the response across multiple chunks. Always buffer and split on `\r\n`.

### Working script
See `sf-mcp-http-wrapper-operational-check.md` in this skill's references for the full operational checklist.
