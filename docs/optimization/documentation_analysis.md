# Documentation Redundancy Analysis Report

**Analysis Date**: 2025-12-31T06:01:27.306050
**Total Files**: 46
**Total Size**: 343.4 KB

> Note: Snapshot captured before the 2025-12-31 documentation cleanup; several files listed below have since been removed or archived (see `docs/archive/legacy-api/` and `03-Deployment.md`).

## Executive Summary

- **Files to Delete**: 6 (13.0%)
- **Files to Archive**: 11 (23.9%)
- **Files to Consolidate**: 3
- **Files to Keep**: 26 (56.5%)

## Recommendations

### 1. DELETE - Obsolete Files (Immediate)

These files are no longer needed and should be deleted:

- `網頁結構.md` (3478 bytes)
  - **Reason**: Temporary Chinese planning docs - superseded by ARCHITECTURE_TREE.md
- `Copilot-Processing.md` (430 bytes)
  - **Reason**: Temporary processing tracker - no longer needed
- `調整結構.md` (2604 bytes)
  - **Reason**: Temporary Chinese planning docs - superseded by ARCHITECTURE_TREE.md
- `結構.md` (2591 bytes)
  - **Reason**: Temporary Chinese planning docs - superseded by ARCHITECTURE_TREE.md
- `結構調整.md` (9025 bytes)
  - **Reason**: Temporary Chinese planning docs - superseded by ARCHITECTURE_TREE.md
- `docs/REMAINING_MIGRATION_PLAN.md` (8488 bytes)
  - **Reason**: Migration completed - all 8 phases done

### 2. ARCHIVE - Historical Reference

Move to `docs/archive/` for historical reference:

- `docs/MEXC_v3_account.md` (2653 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/MEXC_v3_wallet_sub_rebate.md` (3123 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/MEXC_v3_reference_market.md` (3557 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/MEXC_v3.md` (614 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/websocket-1.md` (1477 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/websocket-2.md` (2063 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/MEXC_v3_websocket.md` (3577 bytes)
  - **Reason**: Legacy API docs - move to docs/archive/legacy-api/
- `docs/optimization/coupling_analysis.md` (625 bytes)
  - **Reason**: Raw analysis data - archive to docs/optimization/archive/
- `docs/optimization/module_inventory.md` (11627 bytes)
  - **Reason**: Raw analysis data - archive to docs/optimization/archive/
- `docs/optimization/dead_code_analysis.md` (30976 bytes)
  - **Reason**: Raw analysis data - archive to docs/optimization/archive/
- `docs/optimization/duplication_analysis.md` (6708 bytes)
  - **Reason**: Raw analysis data - archive to docs/optimization/archive/

### 3. CONSOLIDATE - Merge Content

Consolidate into main documentation:

- `docs/00-Jobs.md` (1273 bytes)
  - **Reason**: Legacy deployment docs - consolidate into main deployment guide
- `docs/00-Cloud Run Deploy.md` (4288 bytes)
  - **Reason**: Legacy deployment docs - consolidate into main deployment guide
- `docs/00-Secret-Key.md` (1045 bytes)
  - **Reason**: Legacy deployment docs - consolidate into main deployment guide
