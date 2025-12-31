---
description: 'Repository-wide guidance for defining and executing GitHub Copilot agent tasks with predictable outcomes.'
applyTo: '**'
---

# Copilot Agent Tasks Guidance

- Keep tasks small, testable, and explicitly state acceptance criteria, impacted paths, and constraints.
- Include the relevant prompt file name (under `.github/prompts/`) when assigning a Copilot agent task so the agent starts with the right workflow.
- Before execution, read `.github/copilot-instructions.md` and any matching `.github/instructions/*.instructions.md` (respect `applyTo` scope) to inherit repository rules.
- When a task involves architecture or risk-sensitive changes, instruct the agent to use a short planning step (sequential thinking) and produce a checklist before editing files.
- Prefer minimal diffs that satisfy the task; avoid drive-by refactors outside the declared scope.
- Require targeted validation only for affected areas (formatting, lint, or focused tests), and document what was run.
- Constrain output size: keep generated files under the repository 4000-character limit; split longer outputs if necessary.
- If the task depends on external APIs or tool versions, have the agent fetch current docs via available doc-search tools before proposing changes.
