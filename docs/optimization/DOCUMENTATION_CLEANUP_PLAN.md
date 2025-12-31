# Documentation Cleanup Plan

## Executive Summary

> Status: Phases 1-3 executed on 2025-12-31 — obsolete planning docs removed, legacy API/WebSocket notes archived under `docs/archive/legacy-api/`, deployment guides merged into `docs/03-Deployment.md`.

Analysis of 83 markdown documentation files revealed **7 obsolete files (8.4%)** that can be deleted immediately, **10 legacy files (12.0%)** that should be archived, and **3 deployment guides** that need consolidation. The cleanup will reduce documentation by 20+ files while preserving valuable analysis reports and active guides.

## Analysis Results

### Total Documentation
- **Total Files**: 83
- **Total Size**: ~500 KB
- **Redundant/Obsolete**: 20 files (24.1%)
- **Active/Valuable**: 63 files (75.9%)

### Redundancy Breakdown

| Category | Files | Action | Reason |
|----------|-------|--------|--------|
| Obsolete Migration Plans | 2 | DELETE | All 8 migration phases complete |
| Temporary Tracking | 1 | DELETE | Copilot processing tracker - done |
| Chinese Temporary Docs | 4 | DELETE | Superseded by ARCHITECTURE_TREE.md |
| Legacy API Docs | 8 | ARCHIVE | Pre-migration MEXC/WebSocket docs |
| Raw Analysis Data | 4 | ARCHIVE | Large data files (JSON preferred) |
| Deployment Guides | 3 | CONSOLIDATE | Merge into main deployment doc |

## Cleanup Actions

### Phase 1: DELETE - Obsolete Files (Immediate)

**7 files to delete** - No longer needed after successful migration:

1. **docs/REMAINING_MIGRATION_PLAN.md** (267 lines)
   - Reason: All 8 migration phases completed successfully
   - Status: Obsolete - migration finished in Phase 0-7

2. **Copilot-Processing.md** (430 bytes)
   - Reason: Temporary Copilot processing tracker
   - Status: Kept only when automation requires it; otherwise safe to remove

3. **結構.md** (2.6 KB)
   - Reason: Chinese temporary structure planning doc
   - Status: Superseded by ARCHITECTURE_TREE.md

4. **結構調整.md** (8.9 KB)
   - Reason: Chinese temporary structure adjustment doc
   - Status: Superseded by ARCHITECTURE_TREE.md

5. **網頁結構.md** (3.4 KB)
   - Reason: Chinese temporary web structure doc
   - Status: Superseded by docs/architecture/

6. **調整結構.md** (2.6 KB)
   - Reason: Chinese temporary structure adjustment doc
   - Status: Superseded by ARCHITECTURE_TREE.md

7. **docs/CLEANUP_AND_OPTIMIZATION_PLAN.md** (631 lines)
   - Reason: Original cleanup plan - superseded by Phase reports
   - Status: Phases 1-5 complete, deliverables generated

**Total space freed**: ~20 KB

### Phase 2: ARCHIVE - Historical Reference

**10 files to archive** - Move to `docs/archive/` for reference:

#### Legacy API Documentation (8 files)
Move to `docs/archive/legacy-api/`:

1. **docs/MEXC_v3.md** (614 bytes)
2. **docs/MEXC_v3_account.md** (2.6 KB)
3. **docs/MEXC_v3_reference_market.md** (3.5 KB)
4. **docs/MEXC_v3_wallet_sub_rebate.md** (3.1 KB)
5. **docs/MEXC_v3_websocket.md** (3.5 KB)
6. **docs/websocket-1.md** (1.5 KB)
7. **docs/websocket-2.md** (2.1 KB)
8. **docs/MEXC_API_BALANCE_FIX.md** (historical bug fix)

**Reason**: Pre-migration API documentation - kept for historical reference but not actively used

#### Raw Analysis Data (4 files)
Move to `docs/optimization/archive/`:

1. **docs/optimization/dead_code_analysis.md** (953 lines)
   - Keep: dead_code_analysis.json (structured data)
   - Archive: .md version (human-readable backup)

2. **docs/optimization/module_inventory.md** (266 lines)
   - Keep: module_inventory.json
   - Archive: .md version

3. **docs/optimization/coupling_analysis.md** 
   - Keep: coupling_analysis.json
   - Archive: .md version

4. **docs/optimization/duplication_analysis.md**
   - Keep: duplication_analysis.json
   - Archive: .md version

**Reason**: Large raw data files - JSON versions preferred, Markdown kept as backup

### Phase 3: CONSOLIDATE - Merge Content

**3 deployment guides** - Consolidate into main deployment documentation:

1. **docs/00-Cloud Run Deploy.md** (4.2 KB)
2. **docs/00-Jobs.md** (1.3 KB)
3. **docs/00-Secret-Key.md** (1.1 KB)

**Action**:
- Merge content into **docs/03-Deployment.md** (existing deployment guide)
- Delete original 00-* files after consolidation
- Update references in other docs

### Phase 4: KEEP - Valuable Documentation

**63 files to keep** - Active, valuable documentation:

#### Core Documentation (9 files)
- README.md (root + docs/)
- ARCHITECTURE_TREE.md
- ARCHITECTURE_RULES.md
- CHANGELOG.md
- docs/architecture/ARCHITECTURE.md
- docs/architecture/ARCHITECTURE_DIAGRAM.md
- docs/01-Quickstart-and-Map.md
- docs/02-System-Overview.md
- docs/03-Deployment.md (to be enhanced)

#### Phase Analysis Reports (5 files) ✅
- PHASE2_MODULE_ANALYSIS_REPORT.md
- PHASE3_COUPLING_ANALYSIS_REPORT.md
- PHASE4_DEAD_CODE_ANALYSIS_REPORT.md
- PHASE5_DUPLICATION_ANALYSIS_REPORT.md
- CONTAINER_STARTUP_FIX.md

#### Analysis Tools (5 files) ✅
- analyze_modules.py
- analyze_srp.py
- analyze_coupling.py
- analyze_dead_code.py
- analyze_duplication.py

#### Structured Analysis Data (8 files) ✅
- module_inventory.json
- srp_violations.json
- coupling_analysis.json
- dead_code_analysis.json
- duplication_analysis.json
- (+ corresponding .md files if archived)

#### Strategy & Operations (remaining files)
- docs/04-Operations-and-Tasks.md
- docs/05-Strategies-and-Data.md
- docs/06-API-Compliance-and-Accounts.md
- docs/1-qrl-accumulation-strategy.md
- docs/REFACTORING_ROADMAP.md

## Implementation Plan

### Week 1: Immediate Cleanup (2 hours)

**Day 1 (1 hour) - DELETE Phase**:
```bash
# Delete obsolete migration plans
rm docs/REMAINING_MIGRATION_PLAN.md
rm docs/CLEANUP_AND_OPTIMIZATION_PLAN.md

# Delete temporary tracking
rm Copilot-Processing.md

# Delete Chinese temporary files
rm 結構.md 結構調整.md 網頁結構.md 調整結構.md
```

**Day 2 (1 hour) - ARCHIVE Phase**:
```bash
# Create archive directories
mkdir -p docs/archive/legacy-api
mkdir -p docs/optimization/archive

# Archive legacy API docs
mv docs/MEXC_v3*.md docs/archive/legacy-api/
mv docs/websocket-*.md docs/archive/legacy-api/
mv docs/MEXC_API_BALANCE_FIX.md docs/archive/legacy-api/

# Archive raw analysis data
mv docs/optimization/dead_code_analysis.md docs/optimization/archive/
mv docs/optimization/module_inventory.md docs/optimization/archive/
mv docs/optimization/coupling_analysis.md docs/optimization/archive/
mv docs/optimization/duplication_analysis.md docs/optimization/archive/
```

### Week 2: Consolidation (3 hours)

**Day 1-2 (2 hours) - CONSOLIDATE Phase**:
1. Read 00-* deployment guides
2. Merge content into docs/03-Deployment.md:
   - Add "Cloud Run Deployment" section from 00-Cloud Run Deploy.md
   - Add "Scheduled Jobs" section from 00-Jobs.md
   - Add "Secret Management" section from 00-Secret-Key.md
3. Delete original 00-* files
4. Update cross-references

**Day 3 (1 hour) - VALIDATION**:
1. Update README.md documentation links if needed
2. Verify no broken links
3. Commit changes

## Success Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Files | 83 | 63 | -20 files (24%) |
| Obsolete Files | 7 | 0 | -100% |
| Active Docs | 76 | 63 | Focused |
| Documentation Clarity | Mixed | High | Improved |
| Maintenance Burden | High | Low | Reduced |

## Deliverables

1. **analyze_documentation.py** - Documentation analysis tool
2. **documentation_analysis.json** - Complete analysis data
3. **documentation_analysis.md** - Quick reference report
4. **DOCUMENTATION_CLEANUP_PLAN.md** (this file) - Cleanup execution plan

## Risk Assessment

**Low Risk** 🟢
- Obsolete files clearly identified (migration complete)
- Archive preserves historical content
- No active documentation removed
- Easy rollback if needed

**Mitigation**:
- Create archive/ directories before moving
- Git tracks all deletions (can recover)
- Verify no broken links before finalizing

## Next Steps

1. Review and approve this cleanup plan
2. Execute Phase 1 (DELETE) - immediate
3. Execute Phase 2 (ARCHIVE) - same day
4. Execute Phase 3 (CONSOLIDATE) - following week
5. Update README.md with documentation structure

## Conclusion

Documentation cleanup will remove 24% of files (20 files) that are obsolete, temporary, or redundant after the successful clean architecture migration. This reduces maintenance burden while preserving valuable analysis reports, tools, and active guides. All historical content is archived for reference, and consolidation improves documentation clarity.

**Status**: Ready for execution  
**Risk Level**: 🟢 LOW  
**Time Estimate**: 5 hours over 2 weeks  
**Impact**: Cleaner, more maintainable documentation structure
