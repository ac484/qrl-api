# QRL Trading API - Troubleshooting Guide

This guide helps diagnose and fix common issues with the QRL Trading API.

## 🔴 Balance Display Shows "ERROR" or stuck at fixed values

### Symptoms
- Dashboard shows "ERROR" for QRL/USDT balance
- Balance stuck at fixed values (e.g., USDT always shows 500.00)
- Browser console shows HTTP 401 or 500 errors

### Root Causes & Solutions

#### 1. **API Keys Not Configured** ❌

**Diagnosis:**
- Check browser console (F12 → Console tab)
- Look for: `401 Unauthorized` or "API keys not configured"

**Solution:**
```bash
# For Cloud Run deployment
gcloud run services update qrl-api \
  --set-env-vars MEXC_API_KEY=your_api_key \
  --set-env-vars MEXC_SECRET_KEY=your_secret_key

# For local development
# Create .env file from template
cp .env.example .env

# Edit .env and add your keys
MEXC_API_KEY=your_actual_api_key_here
MEXC_SECRET_KEY=your_actual_secret_key_here
```

**Verification:**
```bash
# Check if environment variables are set
echo $MEXC_API_KEY
echo $MEXC_SECRET_KEY

# For Cloud Run
gcloud run services describe qrl-api --format="value(spec.template.spec.containers[0].env)"
```

#### 2. **Invalid or Expired API Keys** 🔑

**Diagnosis:**
- Browser console shows: "Authentication failed" or "Invalid API key"
- MEXC API returns 401 Unauthorized

**Solution:**
1. Login to MEXC.com
2. Go to: Account → API Management
3. Verify your API key is:
   - ✅ Active (not expired or disabled)
   - ✅ Has IP whitelist configured correctly (or disabled for testing)
   - ✅ Has **Spot Trading** permission enabled

4. If needed, create a new API key:
   - Enable "Spot Trading" permission
   - Disable "Withdrawals" for security
   - Add your IP to whitelist (optional but recommended)
   - Save the key and secret securely

#### 3. **Insufficient API Permissions** ⚠️

**Diagnosis:**
- API key exists and is valid
- Still getting 403 Forbidden errors

**Solution:**
Ensure API key has these permissions:
- ✅ **Read Account Information** (required)
- ✅ **Spot Trading** (required for balance queries)
- ❌ **Withdrawals** (not needed, keep disabled for security)

#### 4. **Network/CORS Issues** 🌐

**Diagnosis:**
- Browser console shows CORS errors
- Network tab shows failed requests

**Solution:**
```bash
# Check if API is accessible
curl https://your-app.run.app/health
curl https://your-app.run.app/account/balance

# Should return JSON, not HTML error page
```

#### 5. **Account Actually Has Zero Balance** 💰

**Diagnosis:**
- API calls succeed (HTTP 200)
- Response shows balances but values are "0"

**Solution:**
1. Login to MEXC.com
2. Check your actual QRL/USDT balance
3. If zero, deposit or trade to get some balance
4. Refresh dashboard

---

## 🔴 Sub-Accounts Not Loading

### Symptoms
- Sub-account dropdown only shows "主帳戶 (Main)"
- Console shows "Sub-account access requires broker permissions"

### Root Causes & Solutions

#### 1. **Not a Broker Account** 🏦

**Diagnosis:**
- Console message: "This feature is only available for MEXC broker accounts"
- `/account/sub-accounts` returns empty list

**Explanation:**
- Sub-account management is a **broker-only feature**
- Regular spot trading accounts cannot access sub-accounts
- This is a MEXC platform limitation, not a bug

**Solution:**
- If you need sub-accounts, contact MEXC to upgrade to a broker account
- For regular accounts, this feature will remain unavailable
- The main account will still work normally

#### 2. **API Key Lacks Broker Permissions** 🔐

**Solution:**
1. Ensure you have a broker account
2. Regenerate API key with broker permissions
3. Update environment variables with new key

#### 3. **Querying Specific Sub-Account Balance** 📊

**New Feature:**
You can now query a specific sub-account's balance using either email or ID:

```bash
# Query by email
curl "https://your-app.run.app/account/sub-account/balance?email=sub@example.com"

# Query by ID (for sub-accounts without email)
curl "https://your-app.run.app/account/sub-account/balance?sub_account_id=123456"

# Query with both (API will use both parameters)
curl "https://your-app.run.app/account/sub-account/balance?email=sub@example.com&sub_account_id=123456"
```

**Note:**
- Not all sub-accounts have email addresses
- Some sub-accounts only have IDs
- The API supports both identifiers for flexibility
- At least one identifier (email or ID) must be provided

---

## 🔴 Bot Not Trading / Status Shows "stopped"

### Symptoms
- Dashboard shows bot status: "stopped" or "paused"
- No trades executing even when conditions are met

### Solution

Use the `/control` endpoint to start the bot:

```bash
# Start the bot
curl -X POST https://your-app.run.app/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start", "reason": "Manual start from admin"}'

# Pause the bot
curl -X POST https://your-app.run.app/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pause", "reason": "Market maintenance"}'

# Stop the bot
curl -X POST https://your-app.run.app/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop", "reason": "End of trading session"}'
```

---

## 🔧 Debugging Steps

### 1. **Enable Browser Console Logging** 📊

**Steps:**
1. Open dashboard in browser
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Look for log messages starting with:
   - `[FETCH]` - API request logs
   - `===` - Section markers for different operations
   - `❌` - Error indicators
   - `✅` - Success indicators

**Example healthy logs:**
```
=== LOADING ACCOUNT BALANCE ===
[FETCH] Calling /account/balance...
[FETCH] /account/balance - Status: 200 OK
📊 Account balance response: {success: true, balances: {...}}
💰 Available assets: ["QRL", "USDT"]
QRL: {free: 1000, locked: 0, total: 1000}
USDT: {free: 500, locked: 0, total: 500}
✅ Balances loaded successfully
=== END ACCOUNT BALANCE ===
```

**Example error logs:**
```
[FETCH] /account/balance - Status: 401 Unauthorized
❌ API Keys not configured or invalid
Help: Check MEXC_API_KEY and MEXC_SECRET_KEY in Cloud Run environment variables
```

### 2. **Check Network Requests** 🌐

**Steps:**
1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Filter by **XHR** or **Fetch**
4. Refresh the page
5. Click on `/account/balance` request
6. Check:
   - **Status Code**: Should be 200 OK
   - **Response**: Should contain valid JSON with balances
   - **Headers**: Check for CORS or auth errors

### 3. **Verify Backend Health** ⚕️

```bash
# Check service health
curl https://your-app.run.app/health

# Should return:
{
  "status": "healthy",
  "redis_connected": true,
  "mexc_api_available": true,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 4. **Check Cloud Run Logs** 📝

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qrl-api" \
  --limit 50 \
  --format json

# Look for:
# - "Failed to get account balance" errors
# - "API keys not configured" warnings
# - Authentication failures
```

---

## 📋 Pre-Deployment Checklist

Before deploying to Cloud Run, verify:

- [ ] **Environment Variables Set**
  ```bash
  MEXC_API_KEY=<your-key>
  MEXC_SECRET_KEY=<your-secret>
  REDIS_URL=<redis-connection-string>
  ```

- [ ] **MEXC API Key Permissions**
  - [ ] Spot Trading enabled
  - [ ] Read Account Information enabled
  - [ ] API key not expired
  - [ ] IP whitelist configured (if used)

- [ ] **Redis Connection**
  - [ ] Redis instance running
  - [ ] REDIS_URL correct
  - [ ] Network access allowed

- [ ] **Cloud Run Configuration**
  - [ ] Service deployed successfully
  - [ ] Environment variables set in Cloud Run
  - [ ] Proper IAM permissions
  - [ ] Cloud Scheduler configured (if using automation)

---

## 🆘 Getting More Help

If issues persist:

1. **Collect Debug Information:**
   ```bash
   # Browser console logs
   # Network tab HAR file
   # Cloud Run logs
   # Error messages
   ```

2. **Check MEXC API Status:**
   - Visit: https://www.mexc.com/support/announcement
   - Look for API maintenance or issues

3. **Verify Configuration:**
   ```bash
   # Test MEXC API directly
   curl https://api.mexc.com/api/v3/ping
   curl https://api.mexc.com/api/v3/time
   ```

4. **Create GitHub Issue:**
   - Include error messages
   - Include browser console logs
   - Include steps to reproduce
   - Redact any sensitive information (API keys, secrets)

---

## 📚 Additional Resources

- [MEXC API Documentation](https://mxcdevelop.github.io/apidocs/spot_v3_en/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Project README](./README.md)
- [Environment Variables Guide](./.env.example)

---

**Last Updated:** 2024-12-27
**Version:** 1.0.0
