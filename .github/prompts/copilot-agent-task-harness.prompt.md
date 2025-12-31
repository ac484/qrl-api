---
description: 'Structured harness for GitHub Copilot agent tasks in this repo, ensuring scoped execution, planning, and validation.'
mode: 'agent'
tools: ['terminal', 'files']
---

# Copilot Agent Task Harness

## Mission
Execute a single repository task with minimal diffs while honoring `.github/copilot-instructions.md` and any matching `.github/instructions/*.instructions.md` scopes.

## Scope & Preconditions
- Task metadata must include a short title, goal, affected paths, and acceptance criteria.
- If the task is high-risk or ambiguous, pause and request clarification before editing.

## Inputs
- ${input:task_title}
- ${input:task_goal}
- ${input:affected_paths:"List of folders/files to touch"}
- ${input:acceptance_criteria:"Bullets the change must satisfy"}

## Workflow
1) **Load context**: read repo-wide instructions and any scoped instruction files for the affected paths. Note required tools/tests.
2) **Plan briefly**: list 3–5 steps (or a checkbox list) covering analysis, edits, and validation. Keep within scope; avoid drive-by refactors.
3) **Execute**: apply the smallest possible edits in the specified paths, keeping each new/updated file under 4000 characters.
4) **Validate**: run only the necessary checks for touched areas (e.g., `make lint` or targeted tests). If skipped, state why.
5) **Summarize**: report what changed, what was validated, and any follow-ups or risks.

## Output Expectations
- Diff summary grouped by file, describing purpose of each change.
- Validation log (commands run or rationale for skipping).
- Outstanding questions or blockers, if any.

## Quality Assurance
- Confirm all acceptance criteria are met.
- Ensure no edits outside `${input:affected_paths}` unless explicitly approved.
- Remove temporary files; adhere to repository formatting and tooling guidance.
