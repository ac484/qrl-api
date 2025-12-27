# Sub-Account Usage Guide

This guide explains how to use the sub-account features in QRL Trading API.

## Overview

MEXC broker accounts can have multiple sub-accounts. This API provides flexible ways to query sub-account information and balances.

**Important**: Sub-account features require a MEXC broker account with appropriate API permissions.

## Features

### 1. List All Sub-Accounts

Get a list of all your sub-accounts:

**Endpoint**: `GET /account/sub-accounts`

**Example**:
```bash
curl https://your-app.run.app/account/sub-accounts
```

**Response**:
```json
{
  "success": true,
  "sub_accounts": [
    {
      "email": "sub1@example.com",
      "id": "123456",
      "status": "active"
    },
    {
      "id": "789012",
      "status": "active"
    }
  ],
  "count": 2,
  "timestamp": "2024-12-27T10:30:00.000Z"
}
```

**Note**: Some sub-accounts have email, some only have ID. Both are supported.

### 2. Query Sub-Account Balance

Get balance for a specific sub-account using email, ID, or both.

**Endpoint**: `GET /account/sub-account/balance`

**Query Parameters**:
- `email` (optional): Sub-account email address
- `sub_account_id` (optional): Sub-account ID

**Note**: At least one parameter must be provided.

#### Option A: Query by Email

For sub-accounts that have email addresses:

```bash
curl "https://your-app.run.app/account/sub-account/balance?email=sub1@example.com"
```

#### Option B: Query by ID

For sub-accounts that only have IDs:

```bash
curl "https://your-app.run.app/account/sub-account/balance?sub_account_id=123456"
```

#### Option C: Query by Both

For maximum precision, provide both identifiers:

```bash
curl "https://your-app.run.app/account/sub-account/balance?email=sub1@example.com&sub_account_id=123456"
```

**Response**:
```json
{
  "success": true,
  "sub_account": {
    "email": "sub1@example.com",
    "id": "123456"
  },
  "balance": {
    "balances": [
      {
        "asset": "QRL",
        "free": "1000.5000",
        "locked": "0.0000"
      },
      {
        "asset": "USDT",
        "free": "500.00",
        "locked": "0.00"
      }
    ]
  },
  "timestamp": "2024-12-27T10:30:00.000Z"
}
```

## Configuration

### Environment Variables

Add these to your `.env` file or Cloud Run environment variables:

```bash
# Required for all API access
MEXC_API_KEY=your_broker_api_key
MEXC_SECRET_KEY=your_broker_secret_key

# Optional: Default sub-account to query
SUB_ACCOUNT_EMAIL=default-sub@example.com
SUB_ACCOUNT_ID=123456
```

**Notes**:
- `SUB_ACCOUNT_EMAIL` and `SUB_ACCOUNT_ID` are optional
- They can be used as default values if your application needs one
- Not all sub-accounts have email - some only have IDs
- The API endpoints accept parameters dynamically

### API Key Requirements

Your MEXC API key must have:
- ✅ **Broker Account** status
- ✅ **Read Account Information** permission
- ✅ **Spot Trading** permission (for balance queries)
- ❌ **Withdrawals** (not needed, keep disabled for security)

## Error Handling

### Common Errors

#### 1. Missing API Keys (401)
```json
{
  "error": "API keys not configured",
  "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
  "help": "Check Cloud Run environment variables or .env file"
}
```

**Solution**: Configure your API keys in environment variables.

#### 2. Missing Identifier (400)
```json
{
  "error": "Missing identifier",
  "message": "Either email or sub_account_id must be provided",
  "help": "Add ?email=xxx@example.com or ?sub_account_id=123456 to the request"
}
```

**Solution**: Provide at least one identifier (email or ID).

#### 3. Insufficient Permissions (403)
```json
{
  "error": "Insufficient permissions",
  "message": "Sub-account access requires broker permissions",
  "help": "This feature is only available for MEXC broker accounts"
}
```

**Solution**: Ensure you have a broker account and proper API permissions.

## Integration Examples

### Python Example

```python
import httpx
import asyncio

async def get_sub_account_balance(email=None, sub_account_id=None):
    """Get sub-account balance"""
    base_url = "https://your-app.run.app"
    
    # Build query parameters
    params = {}
    if email:
        params["email"] = email
    if sub_account_id:
        params["sub_account_id"] = sub_account_id
    
    if not params:
        raise ValueError("Must provide email or sub_account_id")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/account/sub-account/balance",
            params=params
        )
        response.raise_for_status()
        return response.json()

# Usage
async def main():
    # Query by email
    result1 = await get_sub_account_balance(email="sub@example.com")
    
    # Query by ID
    result2 = await get_sub_account_balance(sub_account_id="123456")
    
    # Query by both
    result3 = await get_sub_account_balance(
        email="sub@example.com",
        sub_account_id="123456"
    )
    
    print(result1)

asyncio.run(main())
```

### JavaScript/TypeScript Example

```typescript
async function getSubAccountBalance(
  email?: string,
  subAccountId?: string
): Promise<any> {
  const baseUrl = "https://your-app.run.app";
  
  // Build query parameters
  const params = new URLSearchParams();
  if (email) params.append("email", email);
  if (subAccountId) params.append("sub_account_id", subAccountId);
  
  if (params.toString() === "") {
    throw new Error("Must provide email or sub_account_id");
  }
  
  const response = await fetch(
    `${baseUrl}/account/sub-account/balance?${params.toString()}`
  );
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  
  return await response.json();
}

// Usage
async function main() {
  // Query by email
  const result1 = await getSubAccountBalance("sub@example.com");
  
  // Query by ID
  const result2 = await getSubAccountBalance(undefined, "123456");
  
  // Query by both
  const result3 = await getSubAccountBalance("sub@example.com", "123456");
  
  console.log(result1);
}

main();
```

## Dashboard Integration

The dashboard automatically loads sub-accounts in the account selector dropdown:

1. Open dashboard: `https://your-app.run.app/dashboard`
2. If you have sub-accounts, they will appear in the dropdown
3. Select a sub-account to switch views (if implemented)

**Current Status**: The dropdown is displayed, but switching functionality is not yet implemented. This is a future enhancement.

## Troubleshooting

For detailed troubleshooting, see [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

**Quick Links**:
- [Sub-Accounts Not Loading](../TROUBLESHOOTING.md#-sub-accounts-not-loading)
- [API Key Configuration](../TROUBLESHOOTING.md#api-keys-not-configured-)
- [Debugging Steps](../TROUBLESHOOTING.md#-debugging-steps)

## Best Practices

1. **Use IDs when available**: Sub-account IDs are more stable than emails
2. **Cache sub-account list**: Don't query the list on every request
3. **Handle errors gracefully**: Not all accounts have broker permissions
4. **Validate inputs**: Always check that at least one identifier is provided
5. **Monitor API usage**: Broker APIs may have different rate limits

## Limitations

- **Broker-only feature**: Regular spot accounts cannot access sub-accounts
- **Read-only**: This API only queries balances, not manages sub-accounts
- **No transfers**: Sub-account fund transfers must be done via MEXC web interface
- **Rate limits**: Broker API endpoints may have different rate limits than spot

## Future Enhancements

Planned improvements:
- [ ] Dashboard sub-account switching functionality
- [ ] Sub-account balance history tracking
- [ ] Aggregated balance view across all sub-accounts
- [ ] Sub-account trade history
- [ ] Real-time balance updates via WebSocket

## Support

If you encounter issues:
1. Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
2. Review browser console logs (F12)
3. Verify your broker account status with MEXC
4. Create a [GitHub Issue](https://github.com/7Spade/qrl-api/issues/new)

---

**Last Updated**: 2024-12-27
**Version**: 1.0.0
