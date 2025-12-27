# QRL Trading API - Documentation Index

This index helps you navigate the documentation for the QRL Trading API project.

## 📚 Quick Start

New to the project? Start here:

1. **[README.md](README.md)** - Comprehensive project documentation, features, and setup guide
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - High-level project overview and architecture

## 🚀 Deployment & Setup

Deploy the trading bot to Google Cloud:

- **[deployment.md](deployment.md)** - Complete Cloud Build and Cloud Run deployment guide
- **[Cloud Run Deploy.md](Cloud%20Run%20Deploy.md)** - Quick Cloud Run deployment instructions
- **[scheduler.md](scheduler.md)** - Cloud Scheduler configuration for automated trading
- **[REDIS_CLOUD_SETUP.md](REDIS_CLOUD_SETUP.md)** - Redis Cloud setup and connection guide

## 🏗️ Architecture & Technical Details

Understand the system architecture:

- **[ARCHITECTURE_CHANGES.md](ARCHITECTURE_CHANGES.md)** - Visual diagrams and architecture documentation
- **[MEXC_API_COMPLIANCE.md](MEXC_API_COMPLIANCE.md)** - MEXC API integration and compliance verification
- **[mexc-dev-url.md](mexc-dev-url.md)** - MEXC API reference URLs

## 🔧 Important Fixes & Issues

Historical fixes and solutions:

- **[POSITION_DISPLAY_FIX.md](POSITION_DISPLAY_FIX.md)** - Complete documentation of position display fix
- **[DATA_SOURCE_STRATEGY.md](DATA_SOURCE_STRATEGY.md)** - Correct data source strategy (API vs Redis)
- **[PR8_FIX_SUMMARY.md](PR8_FIX_SUMMARY.md)** - PR8 fix summary
- **[PR8修復說明.md](PR8修復說明.md)** - PR8 fix explanation (Chinese)

## 📈 Trading Strategy

Learn about the trading strategy:

- **[qrl-accumulation-strategy.md](qrl-accumulation-strategy.md)** - Detailed QRL accumulation strategy and economic analysis

## 📋 Documentation Overview

| Document | Purpose | Lines | Priority |
|----------|---------|-------|----------|
| README.md | Main documentation | 2116 | ⭐⭐⭐ Must Read |
| PROJECT_SUMMARY.md | Project overview | 291 | ⭐⭐⭐ Must Read |
| deployment.md | Deployment guide | 232 | ⭐⭐ Important |
| scheduler.md | Scheduler setup | 315 | ⭐⭐ Important |
| ARCHITECTURE_CHANGES.md | Architecture docs | 196 | ⭐⭐ Important |
| POSITION_DISPLAY_FIX.md | Position fix details | 177 | ⭐ Reference |
| DATA_SOURCE_STRATEGY.md | Data strategy | 174 | ⭐ Reference |
| MEXC_API_COMPLIANCE.md | API compliance | 197 | ⭐ Reference |
| REDIS_CLOUD_SETUP.md | Redis setup | 165 | ⭐ Reference |
| qrl-accumulation-strategy.md | Trading strategy | 1357 | 💡 Strategy |
| Cloud Run Deploy.md | Quick deploy | 49 | Reference |
| mexc-dev-url.md | API URLs | 12 | Reference |
| PR8_FIX_SUMMARY.md | PR8 fix | 107 | Reference |
| PR8修復說明.md | PR8 fix (CN) | 78 | Reference |

## 🗂️ Documentation Structure

```
docs/
├── INDEX.md (This file)
│
├── Getting Started
│   ├── README.md
│   └── PROJECT_SUMMARY.md
│
├── Deployment
│   ├── deployment.md
│   ├── Cloud Run Deploy.md
│   ├── scheduler.md
│   └── REDIS_CLOUD_SETUP.md
│
├── Architecture
│   ├── ARCHITECTURE_CHANGES.md
│   ├── MEXC_API_COMPLIANCE.md
│   └── mexc-dev-url.md
│
├── Fixes & Issues
│   ├── POSITION_DISPLAY_FIX.md
│   ├── DATA_SOURCE_STRATEGY.md
│   ├── PR8_FIX_SUMMARY.md
│   └── PR8修復說明.md
│
└── Strategy
    └── qrl-accumulation-strategy.md
```

## 🧹 Recent Cleanup

**Last Updated:** 2025-12-27

We recently cleaned up duplicate, outdated, and useless documentation:

### Removed Files (12)
- ❌ DASHBOARD_FIX.md - Duplicate (replaced by DATA_SOURCE_STRATEGY.md)
- ❌ DASHBOARD_GUIDE.md - Duplicate dashboard info
- ❌ DASHBOARD_PREVIEW.md - Outdated preview
- ❌ DEBUGGING_GUIDE.md - Outdated debugging info
- ❌ FINAL_FIX_SUMMARY.md - Duplicate summary
- ❌ FIX_README.md - Duplicate quick reference
- ❌ implementation.md - Outdated Flask implementation
- ❌ ximplementation.md - Draft/duplicate
- ❌ SUMMARY.md - Duplicate
- ❌ 0.md, 1.md, 2.md - Temporary/draft files

All essential information has been preserved in the remaining documents.

## 📖 Reading Guide

### For New Developers
1. Start with **README.md** for project overview
2. Read **PROJECT_SUMMARY.md** for architecture understanding
3. Follow **deployment.md** to deploy your first instance

### For Deployment Engineers
1. **deployment.md** - Complete deployment guide
2. **scheduler.md** - Scheduler configuration
3. **REDIS_CLOUD_SETUP.md** - Redis setup

### For Troubleshooting
1. **POSITION_DISPLAY_FIX.md** - Position display issues
2. **DATA_SOURCE_STRATEGY.md** - Data source best practices
3. **MEXC_API_COMPLIANCE.md** - API integration verification

### For Strategy Understanding
1. **qrl-accumulation-strategy.md** - Complete strategy analysis
2. **README.md** - Trading bot logic overview

## 🔍 Search Tips

- Use `grep -r "keyword" docs/` to search across all docs
- Most files use Markdown headers (`#`, `##`, `###`) for structure
- Code examples are in fenced code blocks (```)
- Important sections are marked with emojis (🔥, ⚠️, ✅, etc.)

## 📝 Contributing

When adding new documentation:
- Place it in the appropriate category
- Update this INDEX.md with the new file
- Use clear, descriptive filenames
- Include a purpose statement at the top
- Add it to the table above with line count and priority

## 💡 Need Help?

- Check the appropriate documentation file first
- Search for error messages in existing docs
- Review POSITION_DISPLAY_FIX.md for common issues
- Consult MEXC_API_COMPLIANCE.md for API questions

---

**Total Documentation:** 14 files | ~5,500 lines of organized content
