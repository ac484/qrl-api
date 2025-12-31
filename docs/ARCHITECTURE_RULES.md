## Architecture Guardrails (Progressive Migration)

These rules formalize the migration targets described in `ARCHITECTURE_TREE.md` and `architecture/ARCHITECTURE.md`. They apply to **new code under `src/app`** so we can evolve safely without breaking the legacy runtime.

### Scope
- Covers Python modules inside `src/app/**`.
- Legacy folders (`api/`, `services/`, `repositories/`, `infrastructure/` root) remain untouched until migrated.

### Hard Limits
- **File size:** every `.py` file in `src/app` must be **≤ 4000 bytes**.
- **Forbidden filenames in `src/app`:** `client.py`, `core.py`, `utils.py` (split responsibilities instead).
- **One file, one responsibility:** prefer behavior-based filenames (`get_price.py`, `execute_trade.py`).

### Layering Reminders
- `interfaces/http` must not import infrastructure.
- `domain` stays framework-agnostic; no Redis/MEXC details.
- `application` talks to `domain` ports and composes use cases.
- `infrastructure` only implements ports; `bootstrap.py` is the assembly point.

### Checks
- Run the guard script to enforce limits:
  ```bash
  python architecture_guard.py --base src/app
  ```
- The guard is wired into `tests/validation_framework.py` so CI can detect violations early.

### Goal
Keep migrations incremental and safe: add new code in the target tree with small, testable files while the legacy runtime keeps working. Remove legacy files only after their responsibilities are covered in `src/app`.
