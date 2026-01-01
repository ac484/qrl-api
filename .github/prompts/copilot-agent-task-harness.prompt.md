---
description: 'Structured harness for GitHub Copilot agent tasks in this repo, ensuring scoped execution, planning, and validation.'
mode: 'agent'
tools: ['terminal', 'files']
---

# Copilot Agent Task Harness

Execute repository tasks with surgical precision, comprehensive planning, and thorough validation.

## Mission
Execute a single, well-defined repository task with minimal diffs while strictly adhering to:
- `.github/copilot-instructions.md` (repository-wide conventions)
- `.github/instructions/*.instructions.md` (scoped to affected paths)
- Repository architecture patterns and coding standards

## Scope & Preconditions

### Task Requirements
Task metadata **must** include all of the following:
- **Title**: Short, descriptive name (≤50 characters)
- **Goal**: Clear objective (1-2 sentences)
- **Affected Paths**: Specific files/directories to modify
- **Acceptance Criteria**: Testable success conditions
- **Constraints**: Technical limits, dependencies, requirements

### Risk Assessment
Before proceeding, evaluate:
- **High-risk tasks** (architecture changes, security, data migration): Require detailed planning
- **Ambiguous tasks** (unclear requirements, multiple interpretations): Request clarification
- **Complex tasks** (>5 files affected, cross-module changes): Break into subtasks if possible

If task is high-risk or ambiguous, **pause and request clarification** before editing.

## Inputs

Required inputs for task execution:

- **${input:task_title}**: Brief, descriptive task name
- **${input:task_goal}**: What the task accomplishes and why
- **${input:affected_paths:"src/api/market_routes.py, tests/api/test_market.py"}**: Specific files/directories
- **${input:acceptance_criteria:"- Cache hit rate >80%\n- Response time <100ms\n- Tests pass"}**: Measurable success criteria
- **${input:constraints:"Max 4000 chars per file, use existing RedisClient"}** (optional): Technical constraints

## Workflow

### Phase 1: Context Loading (Mandatory)

**Load all required context before making any changes:**

1. **Read repository instructions**: `.github/copilot-instructions.md`
   - Note architecture patterns (3-layer: API → Domain → Infrastructure)
   - Review coding standards (Python: type hints, async/await, Pydantic)
   - Identify required tools (black, ruff, mypy, pytest)

2. **Load scoped instructions**: `.github/instructions/*.instructions.md`
   - Match `applyTo` patterns against affected paths
   - Review domain-specific guidelines (e.g., python.instructions.md)
   - Note special requirements (file size limits, patterns to follow)

3. **Analyze existing code**:
   - Read all files in `${input:affected_paths}`
   - Identify current patterns and conventions
   - Locate related tests and dependencies
   - Map integration points and side effects

4. **Document context**:
   ```markdown
   ## Context Summary
   - Repository pattern: [pattern identified]
   - Affected modules: [list modules]
   - Key dependencies: [list deps]
   - Test strategy: [test approach]
   - Validation tools: [tools to use]
   ```

**Context Loading Checklist:**
- [ ] Repository instructions read
- [ ] Scoped instructions identified and reviewed
- [ ] All affected files examined
- [ ] Related tests located
- [ ] Dependencies mapped
- [ ] Integration points identified

### Phase 2: Planning (Mandatory)

**Create detailed execution plan:**

1. **Analysis steps**: What needs to be understood before coding
2. **Design decisions**: Patterns to use, approach to take
3. **Implementation steps**: Specific changes to specific files
4. **Testing strategy**: What tests to write/update, how to verify
5. **Validation approach**: Linting, formatting, type checking

**Plan Format:**
```markdown
## Execution Plan

### Analysis
- Review [specific aspect] in [file]
- Identify [pattern/dependency] in [location]
- Understand [integration point]

### Design
- Follow [repository pattern] for [functionality]
- Use [existing component] for [purpose]
- Apply [coding standard] to [implementation]

### Implementation
1. Modify `[file1]`:
   - Add [specific change]
   - Update [specific section]
   - Rationale: [why this change]

2. Update `[file2]`:
   - Integrate [new functionality]
   - Preserve [existing behavior]
   - Rationale: [why this change]

3. Add/Update tests in `[test_file]`:
   - Test [functionality aspect]
   - Cover [edge cases]
   - Verify [acceptance criterion]

### Validation
- Run: `make fmt` (black formatting)
- Run: `make lint` (ruff linting)
- Run: `make type` (mypy type checking)
- Run: `pytest [test_file]` (targeted tests)
- Verify: All acceptance criteria met

### Risks
- [Potential issue 1]: [mitigation]
- [Potential issue 2]: [mitigation]
```

**Planning Checklist:**
- [ ] All affected files identified
- [ ] Changes scoped to minimum necessary
- [ ] Design follows repository patterns
- [ ] Test strategy defined
- [ ] Validation approach specified
- [ ] Risks identified with mitigations

### Phase 3: Execution (Systematic)

**Apply changes following plan:**

1. **Make surgical edits**:
   - Modify only what's necessary for the task
   - Preserve existing code style and patterns
   - Follow repository conventions (see copilot-instructions.md)
   - Keep each file under 4000 characters

2. **Maintain quality**:
   - Use meaningful variable/function names
   - Add docstrings for new functions (PEP 257 for Python)
   - Include type hints (Python: mandatory)
   - Document complex logic with inline comments

3. **Test incrementally**:
   - Verify syntax after each file edit
   - Run targeted tests after logical changes
   - Fix issues immediately before proceeding

4. **Track changes**:
   ```markdown
   ## Changes Made
   
   ### Modified: `src/api/market_routes.py`
   - Added Redis caching to `/market/ticker` endpoint
   - Integrated with existing RedisClient pattern
   - Added cache TTL of 5 seconds
   
   ### Updated: `tests/api/test_market.py`
   - Added test_market_ticker_cache_hit
   - Added test_market_ticker_cache_miss
   - Verified cache TTL behavior
   ```

**Execution Checklist:**
- [ ] Changes follow plan
- [ ] Code style matches repository
- [ ] File size limits respected
- [ ] No unrelated changes made
- [ ] Tests updated/added
- [ ] Complex logic documented

### Phase 4: Validation (Comprehensive)

**Run all necessary checks:**

1. **Code Quality**:
   ```bash
   # Format code
   make fmt
   
   # Check linting
   make lint
   
   # Verify type hints
   make type
   ```

2. **Functionality**:
   ```bash
   # Run affected tests
   pytest tests/api/test_market.py -v
   
   # Run broader test suite if needed
   pytest tests/api/ -v
   ```

3. **Acceptance Criteria**:
   - [ ] Criterion 1: [verification method] → [PASS/FAIL]
   - [ ] Criterion 2: [verification method] → [PASS/FAIL]
   - [ ] Criterion 3: [verification method] → [PASS/FAIL]

4. **Manual Verification** (if applicable):
   - Start application: `uvicorn main:app --reload`
   - Test endpoint: `curl http://localhost:8000/market/ticker`
   - Verify behavior: [expected vs actual]

**Document Results**:
```markdown
## Validation Results

### Code Quality
- ✅ Formatting: `make fmt` - PASSED
- ✅ Linting: `make lint` - PASSED
- ✅ Type Checking: `make type` - PASSED

### Testing
- ✅ Unit Tests: `pytest tests/api/test_market.py` - 5 passed
- ✅ Integration Tests: `pytest tests/api/` - 23 passed

### Acceptance Criteria
- ✅ Cache hit rate >80%: Verified in tests
- ✅ Response time <100ms: Measured at 45ms avg
- ✅ All tests pass: 23/23 passed

### Manual Verification
- ✅ Endpoint responds correctly
- ✅ Cache behaves as expected
- ✅ No performance regression
```

**Validation Checklist:**
- [ ] All code quality checks passed
- [ ] All tests pass (existing + new)
- [ ] All acceptance criteria verified
- [ ] Manual testing completed (if needed)
- [ ] No unintended side effects
- [ ] Performance acceptable

### Phase 5: Summary and Completion

**Provide comprehensive summary:**

1. **Changes Summary**:
   ```markdown
   ## Summary
   
   ### Files Modified (2)
   - `src/api/market_routes.py`: Added Redis caching to ticker endpoint
   - `tests/api/test_market.py`: Added cache behavior tests
   
   ### Functionality Added
   - Redis caching with 5-second TTL
   - Cache hit/miss logging
   - Performance improvement: 45ms avg response time
   
   ### Tests Added
   - test_market_ticker_cache_hit
   - test_market_ticker_cache_miss
   - test_market_ticker_cache_expiry
   ```

2. **Validation Report**:
   - List all checks performed
   - Report all results (pass/fail)
   - Document any issues found and resolved

3. **Acceptance Verification**:
   - [ ] All criteria met: YES/NO
   - [ ] Deviations from plan: [list or "None"]
   - [ ] Follow-up tasks: [list or "None"]

4. **Risks and Notes**:
   - Outstanding issues: [list or "None"]
   - Future improvements: [suggestions]
   - Documentation needs: [any doc updates needed]

## Output Expectations

### Required Outputs

1. **Context Summary**: What was reviewed and understood
2. **Execution Plan**: Detailed step-by-step plan (before coding)
3. **Changes Report**: File-by-file description of modifications
4. **Validation Log**: Commands run and results
5. **Acceptance Verification**: Each criterion checked
6. **Final Summary**: Overall outcome and next steps

### Format Example

```markdown
# Task: [Title]

## 1. Context Summary
[What was loaded and understood]

## 2. Execution Plan
[Detailed plan before implementation]

## 3. Changes Made
### Modified: `file1.py`
- Change 1: [description]
- Rationale: [why]

### Updated: `file2.py`
- Change 1: [description]
- Rationale: [why]

## 4. Validation Results
### Code Quality
- Formatting: PASSED
- Linting: PASSED
- Type Checking: PASSED

### Testing
- Unit Tests: 5/5 PASSED
- Integration Tests: 23/23 PASSED

### Acceptance Criteria
- [x] Criterion 1: Verified by [method]
- [x] Criterion 2: Verified by [method]
- [x] Criterion 3: Verified by [method]

## 5. Summary
- Changes: [count] files modified
- Tests: [count] added, all passing
- Validation: All checks passed
- Acceptance: All criteria met
- Follow-ups: [any or "None"]

## 6. Deviations & Risks
- Deviations: [any or "None"]
- Outstanding Risks: [any or "None"]
- Recommendations: [any improvements]
```

## Quality Assurance

### Final Verification Checklist

Before marking task complete, verify:

**Scope Compliance:**
- [ ] All changes within `${input:affected_paths}`
- [ ] No unauthorized modifications
- [ ] No drive-by refactoring
- [ ] Changes align with plan

**Code Quality:**
- [ ] Follows repository patterns
- [ ] Adheres to coding standards
- [ ] File size limits respected
- [ ] No temporary files left

**Testing:**
- [ ] All new code tested
- [ ] Existing tests still pass
- [ ] Edge cases covered
- [ ] Integration verified

**Acceptance:**
- [ ] All criteria explicitly verified
- [ ] Verification method documented
- [ ] Results recorded

**Documentation:**
- [ ] Complex logic commented
- [ ] Docstrings added/updated
- [ ] README updated (if needed)
- [ ] Changes documented

**Validation:**
- [ ] Formatting passed
- [ ] Linting passed
- [ ] Type checking passed
- [ ] All tests passed

### Common Issues and Solutions

**Issue**: File exceeds 4000 characters
**Solution**: Split into multiple files or refactor to reduce size

**Issue**: Tests fail after changes
**Solution**: Debug immediately, don't proceed until fixed

**Issue**: Linting errors introduced
**Solution**: Run `make fmt` and `make lint`, fix issues

**Issue**: Scope expanded during implementation
**Solution**: Complete original task, create new task for additional work

**Issue**: Validation skipped
**Solution**: Document specific reason and get approval to skip

## Related Resources

- **Repository Standards**: `.github/copilot-instructions.md`
- **Task Guidance**: `.github/instructions/copilot-agent-tasks.instructions.md`
- **Implementation Guide**: `.github/instructions/task-implementation.instructions.md`
- **Prompt Library**: `.github/prompts/`
