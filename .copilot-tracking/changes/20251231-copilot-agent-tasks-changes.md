<!-- markdownlint-disable-file -->
# Release Changes: Copilot agent task configuration

**Related Plan**: n/a  
**Implementation Date**: 2025-12-31

## Summary

Added repository-level guidance and a reusable prompt to standardize GitHub Copilot agent task execution within this project.

## Changes

### Added

- .github/instructions/copilot-agent-tasks.instructions.md - Defines expectations for scoping, planning, and validating Copilot agent tasks across the repository.
- .github/prompts/copilot-agent-task-harness.prompt.md - Provides a structured harness prompt for running Copilot agent tasks with planning, execution, and validation steps.

### Modified

- None

### Removed

- None

## Release Summary

**Total Files Affected**: 2

### Files Created (2)

- .github/instructions/copilot-agent-tasks.instructions.md - New repository-wide guidance for Copilot agent tasks.
- .github/prompts/copilot-agent-task-harness.prompt.md - New task harness prompt for Copilot agent execution.

### Files Modified (0)

- None

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: None
- **Configuration Updates**: None

### Deployment Notes

No deployment actions required; configuration-only changes.
