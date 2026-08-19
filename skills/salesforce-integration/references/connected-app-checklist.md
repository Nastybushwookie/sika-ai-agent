# Connected App Setup Checklist

1. Navigate to Setup → App Manager → New Connected App
2. Fill in:
   - Connected App Name
   - API Name (auto-generated)
   - Contact Email
   - Logo (optional)
3. Enable OAuth Settings
4. Set Callback URL: `https://<YOUR_DOMAIN>/oauth/salesforce/callback`
5. Add OAuth Scopes:
   - `openid`
   - `api`
   - `refresh_token` (or "Perform requests on your behalf at any time")
6. Save
7. Capture:
   - Consumer Key (client_id)
   - Consumer Secret (client_secret)
8. Note your org URL:
   - Production: `https://login.salesforce.com`
   - Sandbox: `https://test.salesforce.com`