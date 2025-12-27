# Changelog

## [1.2.0] - 2024-12-27

### Added
- 🔧 **Redis Cloud Support**: 
  - New `REDIS_URL` environment variable for Redis Cloud connectivity
  - Automatic fallback to individual Redis parameters if URL not provided
  - Support for `redis://` and `rediss://` (SSL/TLS) connection strings
  - Comprehensive [REDIS_CLOUD_SETUP.md](REDIS_CLOUD_SETUP.md) guide

### Changed
- **Configuration Priority**: 
  - `REDIS_URL` takes precedence over individual Redis parameters
  - Updated `.env.example` to show `REDIS_URL` as primary option
  - Enhanced logging to indicate connection method (URL vs parameters)

### Documentation
- Added Redis Cloud setup guide with examples for Redis Cloud and Upstash
- Updated README.md with Redis Cloud deployment instructions
- Added troubleshooting section for common Redis connection issues

## [1.1.0] - 2024-12-27

### Added
- 📊 **Web Dashboard**: Visual UI at `/dashboard` endpoint
  - Real-time balance display for QRL and USDT
  - Current QRL/USDT price with 24h change percentage
  - Available and locked balance breakdown
  - Total portfolio value calculation
  - Auto-refresh every 30 seconds
  - Manual refresh button
  - Responsive design (desktop/tablet/mobile)
  
- 👥 **Sub-Account Support**:
  - New API endpoint: `GET /account/sub-accounts`
  - Account selector dropdown in dashboard
  - `MEXCClient.get_sub_accounts()` method
  - `MEXCClient.get_sub_account_balance(email)` method
  
- 📚 **Documentation**:
  - `DASHBOARD_GUIDE.md` - Comprehensive dashboard usage guide
  - `DASHBOARD_PREVIEW.md` - Visual preview of dashboard layout

### Changed
- 🔧 **Dependencies**:
  - Removed `aioredis==2.0.1` (integrated into redis-py 5.0+)
  - Added `jinja2==3.1.2` for template rendering
  - Using `redis==5.0.1` with built-in async support

### Technical Details
- Added Jinja2Templates for HTML rendering
- Created `templates/dashboard.html` with modern CSS styling
- Added sub-account API integration with MEXC
- Enhanced main.py with dashboard and sub-account endpoints

## [1.0.0] - 2024-12-27

### Initial Release
- FastAPI + Uvicorn async web framework
- MEXC API v3 integration with httpx
- Redis state management with redis.asyncio
- 6-phase trading bot execution system
- Moving average crossover strategy
- Risk control and position management
- Docker containerization
- Comprehensive API documentation
