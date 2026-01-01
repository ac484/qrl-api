---
description: 'Repository-wide guidance for defining and executing GitHub Copilot agent tasks with predictable outcomes.'
applyTo: '**'
---

# Copilot Agent Tasks Guidance

Comprehensive guidance for creating, executing, and validating GitHub Copilot agent tasks in this repository.

## Core Principles

### Task Definition
- **Small and Focused**: Keep tasks small, testable, and focused on a single objective
- **Explicit Criteria**: State acceptance criteria, impacted paths, and constraints clearly
- **Prompt Integration**: Reference the relevant prompt file (`.github/prompts/`) for workflow guidance
- **Context Inheritance**: Read `.github/copilot-instructions.md` and matching `.github/instructions/*.instructions.md`

### Planning and Execution
- **Risk Assessment**: For architecture or risk-sensitive changes, require planning with sequential thinking
- **Minimal Changes**: Prefer minimal diffs that satisfy requirements; avoid scope creep
- **Checklist-Driven**: Produce executable checklists before editing files
- **Output Constraints**: Keep files under 4000 characters; split if necessary

### Validation and Quality
- **Targeted Testing**: Validate only affected areas (formatting, lint, focused tests)
- **Documentation**: Document what validation was performed and results
- **External Dependencies**: Fetch current docs for external APIs or tools before implementing

## Task Lifecycle Workflow

### 1. Task Definition Phase
**Define clear task parameters:**
- **Title**: Short, descriptive task name (≤50 chars)
- **Goal**: What the task accomplishes (1-2 sentences)
- **Scope**: Specific files, directories, or modules affected
- **Acceptance Criteria**: Testable conditions for success
- **Constraints**: Technical limits, dependencies, or requirements

**Example Task Definition:**
```markdown
Title: Add Redis caching to market data endpoint
Goal: Implement Redis caching for /market/ticker to reduce MEXC API calls
Scope: src/api/market_routes.py, src/infrastructure/redis_client.py
Acceptance: 
  - Cache TTL of 5 seconds
  - Cache hit logged in structured format
  - No breaking changes to API response
Constraints: Must use existing RedisClient pattern
```

### 2. Context Loading Phase
**Load required context before execution:**
1. Read repository-wide instructions (`.github/copilot-instructions.md`)
2. Identify and read scoped instructions matching affected paths
3. Review related code files and patterns
4. Check existing tests for similar functionality
5. Understand dependencies and integration points

**Context Checklist:**
- [ ] Repository instructions read and understood
- [ ] Scoped instructions identified and reviewed
- [ ] Existing patterns in affected files examined
- [ ] Related tests located and reviewed
- [ ] Dependencies and integrations mapped

### 3. Planning Phase
**Create execution plan:**
- List 3-7 specific steps covering analysis, changes, and validation
- Identify files to create, modify, or delete
- Plan validation approach (tests, linting, manual checks)
- Note any risks or edge cases
- Keep plan within defined scope

**Planning Template:**
```markdown
## Execution Plan
1. Analysis: Review current implementation in [files]
2. Design: Plan changes following [pattern/convention]
3. Implement: 
   - Modify [file1] to add [functionality]
   - Update [file2] to integrate [change]
4. Test: Run [specific tests] to validate
5. Validate: Check [formatting/linting] on affected files
6. Document: Update [relevant docs] if needed
```

### 4. Execution Phase
**Apply changes systematically:**
- Follow plan steps in order
- Make minimal, surgical edits
- Maintain existing code style and patterns
- Keep each file under 4000 characters
- Document complex logic with inline comments
- Avoid refactoring unrelated code

**Execution Best Practices:**
- One logical change per file edit
- Test incrementally after each change
- Commit related changes together
- Use descriptive commit messages
- Respect repository coding standards

### 5. Validation Phase
**Verify changes meet requirements:**
- Run targeted tests for affected functionality
- Execute linting on modified files
- Validate against acceptance criteria
- Check for unintended side effects
- Document validation results

**Validation Checklist:**
- [ ] All acceptance criteria met
- [ ] Tests pass (unit, integration as applicable)
- [ ] Linting passes (make lint or equivalent)
- [ ] No unintended changes to unrelated code
- [ ] Documentation updated if needed
- [ ] Changes reviewed against plan

### 6. Completion Phase
**Finalize and document:**
- Summarize what changed (files, functionality)
- Report validation results
- Note any deviations from plan with justification
- Identify follow-up tasks or risks
- Update tracking files if applicable

## Task Patterns and Examples

### Pattern 1: Feature Addition
**Use case**: Adding new functionality to existing module

**Template**:
```markdown
Task: Add [feature] to [module]
Goal: Enable [capability] by implementing [approach]
Files: [specific paths]
Acceptance:
  - [Functional requirement 1]
  - [Functional requirement 2]
  - Tests pass
  - No breaking changes
Steps:
  1. Add [core logic] to [file]
  2. Integrate with [existing component]
  3. Add tests in [test file]
  4. Validate with [validation method]
```

### Pattern 2: Bug Fix
**Use case**: Fixing identified issue

**Template**:
```markdown
Task: Fix [issue] in [component]
Goal: Resolve [problem] by [solution approach]
Files: [affected files]
Root Cause: [brief explanation]
Acceptance:
  - [Bug no longer reproduces]
  - [Existing functionality preserved]
  - [Regression test added]
Steps:
  1. Reproduce issue with [method]
  2. Identify root cause in [location]
  3. Apply fix to [file]
  4. Add regression test
  5. Verify fix resolves issue
```

### Pattern 3: Refactoring
**Use case**: Improving code structure without changing behavior

**Template**:
```markdown
Task: Refactor [component] for [improvement]
Goal: Improve [quality aspect] while preserving behavior
Files: [files to refactor]
Acceptance:
  - [Code quality metric improved]
  - All existing tests pass
  - No behavior changes
  - [Performance maintained/improved]
Steps:
  1. Document current behavior with tests
  2. Apply refactoring to [files]
  3. Verify tests still pass
  4. Check performance unchanged
  5. Update inline documentation
```

### Pattern 4: Documentation Update
**Use case**: Updating technical documentation

**Template**:
```markdown
Task: Update [documentation] for [reason]
Goal: Document [changes/features] accurately
Files: [doc files]
Acceptance:
  - [Accuracy verified]
  - [Examples updated/added]
  - [Links valid]
  - [Formatting correct]
Steps:
  1. Review current documentation
  2. Identify outdated sections
  3. Update content with accurate information
  4. Add/update examples
  5. Verify links and formatting
```

## Best Practices

### Do's ✅
- **Define before executing**: Write clear task definition before starting
- **Load context first**: Read relevant instructions and patterns
- **Plan before coding**: Create step-by-step execution plan
- **Make minimal changes**: Only modify what's necessary for the task
- **Test incrementally**: Validate after each significant change
- **Document validation**: Record what was tested and results
- **Follow conventions**: Use existing code patterns and styles
- **Respect constraints**: Stay within repository limits (file size, etc.)

### Don'ts ❌
- **Scope creep**: Avoid adding features not in acceptance criteria
- **Drive-by refactoring**: Don't refactor unrelated code
- **Skipping validation**: Never skip testing affected functionality
- **Breaking patterns**: Don't introduce new patterns without justification
- **Ignoring instructions**: Always check repository and scoped instructions
- **Large commits**: Avoid mixing unrelated changes in one commit
- **Undocumented changes**: Don't leave complex logic unexplained
- **Blind changes**: Never modify code without understanding context

## Validation Requirements

### Code Quality
- **Linting**: Run `make lint` or equivalent on affected files
- **Formatting**: Ensure code follows repository style (black, ruff for Python)
- **Type checking**: Verify type hints if applicable (mypy for Python)
- **Import organization**: Check import order and grouping

### Testing
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Verify component interactions
- **Edge cases**: Test boundary conditions and error handling
- **Regression tests**: Ensure existing functionality unchanged

### Documentation
- **Inline comments**: Complex logic explained
- **Docstrings**: Functions/classes documented (Python: PEP 257)
- **README updates**: User-facing docs updated if needed
- **API docs**: Endpoint documentation current

### Repository Standards
- **File size**: All files ≤4000 characters (split if needed)
- **Architecture**: Follow three-layer pattern (API → Domain → Infrastructure)
- **Naming**: Use repository conventions (see copilot-instructions.md)
- **Dependencies**: Minimize additions, document if required

## Troubleshooting

### Task Too Large
**Problem**: Task encompasses too many changes
**Solution**: Split into smaller, focused subtasks

**Example**:
```markdown
Original: "Implement user authentication system"
Split into:
  - Task 1: Add user model and database schema
  - Task 2: Implement authentication endpoints
  - Task 3: Add JWT token generation
  - Task 4: Integrate authentication middleware
```

### Unclear Acceptance Criteria
**Problem**: Success conditions ambiguous or untestable
**Solution**: Rewrite criteria as specific, measurable conditions

**Example**:
```markdown
Unclear: "Improve performance"
Clear:
  - Response time ≤100ms for /market/ticker
  - Redis cache hit rate ≥80%
  - No increase in error rate
```

### Scope Creep
**Problem**: Additional work identified during implementation
**Solution**: Document as follow-up task, don't expand current scope

**Example**:
```markdown
Current Task: Add caching to market endpoint
Discovered: Market data transformation could be optimized
Action: Complete caching task, create new task for optimization
```

### Validation Failures
**Problem**: Tests fail or linting errors after changes
**Solution**: Fix issues before proceeding, don't commit broken code

**Process**:
1. Identify specific failure (test name, linting rule)
2. Understand root cause of failure
3. Fix issue in affected code
4. Re-run validation to confirm fix
5. Document fix if complex or non-obvious

## Integration with Repository Tools

### Required Tools
- **Linting**: `make lint` (ruff for Python)
- **Formatting**: `make fmt` (black for Python)
- **Type checking**: `make type` (mypy for Python)
- **Testing**: `make test` (pytest for Python)

### Recommended Workflow
```bash
# Before starting
git checkout -b task/descriptive-name

# During development
make fmt              # Format code
make lint             # Check linting
make type             # Type check
make test             # Run tests

# Before committing
git add [changed files]
git commit -m "descriptive message"
```

### Validation Commands
```bash
# Validate specific files
black --check src/api/market_routes.py
ruff check src/api/market_routes.py
mypy src/api/market_routes.py

# Run targeted tests
pytest tests/api/test_market_routes.py -v
pytest tests/api/test_market_routes.py::test_specific_function
```

## Task Template

Use this template for consistent task definition:

```markdown
# Task: [Concise Title]

## Goal
[1-2 sentences describing what this task accomplishes]

## Scope
**Affected Files**:
- [file/path1]
- [file/path2]

**Affected Modules**:
- [module/component1]
- [module/component2]

## Acceptance Criteria
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]
- [ ] All tests pass
- [ ] Linting passes
- [ ] Documentation updated

## Constraints
- [Technical constraint 1]
- [Repository limit 1 (e.g., file size)]
- [Dependency constraint]

## Execution Plan
1. **Analysis**: [What to analyze]
2. **Implementation**: [What to implement]
3. **Testing**: [What to test]
4. **Validation**: [How to validate]
5. **Documentation**: [What to document]

## Validation Checklist
- [ ] Context loaded (instructions, patterns)
- [ ] Plan created and reviewed
- [ ] Changes implemented
- [ ] Tests written/updated
- [ ] Linting passed
- [ ] Documentation updated
- [ ] Acceptance criteria met
- [ ] Changes reviewed

## Notes
[Any additional context, risks, or considerations]
```

## Related Resources

- **Repository Instructions**: `.github/copilot-instructions.md`
- **Prompt Library**: `.github/prompts/`
- **Scoped Instructions**: `.github/instructions/`
- **Task Harness**: `.github/prompts/copilot-agent-task-harness.prompt.md`
- **Implementation Guide**: `.github/instructions/task-implementation.instructions.md`
