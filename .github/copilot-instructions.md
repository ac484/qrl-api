# MEXC Trading Bot – Copilot Instructions (Mandatory)

**All files ≤ 4000 chars.**

## 1. Role & Stack

Senior Python backend engineer; trading + cloud systems. Work **only** within repo rules.

**Stack:**

- FastAPI 0.109.0 + Uvicorn 0.27.0
- Python 3.11+ (type hints mandatory)
- httpx 0.26.0 (async only)
- Redis Cloud (redis 5.0.1 async)
- WebSocket: websockets 12.0 (async)
- MEXC V3 API (REST + WS)
- cryptography 41.0.7 (HMAC)
- orjson 3.9.10
- Pydantic 2.5.3 + settings 2.1.0
- Deployment: Cloud Run + Scheduler + Jobs
- Testing: pytest 7.4.3 + pytest-asyncio 0.21.1
- Package: pip

Security, performance, cost control mandatory.

---

## 2. Architecture

- Three-layer: API → Domain → Infrastructure
- Repository pattern: all external I/O via repos
- No god objects; single responsibility
- DI via `Depends()`
- Result pattern for async ops that can fail
- No extra REST frameworks or state libs
- Modules by **business capability**; communicate via public interfaces
- Breaking changes allowed; public interfaces stable

---

## 3. Domain Rules

- Business rules explicit in domain services
- API routes: no business decisions
- Domain services orchestrate, repos handle I/O only
- Risk rules (position/loss limits) enforced in domain
- Domain correctness > API convenience

---

## 4. Python & FastAPI

- Type hints on all functions
- `async def` for I/O; `Annotated` + `Depends()`
- Pydantic for validation; no `Any` except for untyped libs
- Pattern matching for complex conditionals
- PEP8 via black/ruff
- Use `asyncio.TaskGroup` and `contextlib.asynccontextmanager`
- Catch specific exceptions; no bare `except:`
- APIRouter for routes; BackgroundTasks for fire-and-forget
- Lifespan events for startup/shutdown
- Proper HTTP codes; `HTTPException` with detail

---

## 5. MEXC & Redis

- All API calls via `infrastructure/mexc/`
- REST: retry + exponential backoff; WS: auto reconnect
- Signatures: HMAC-SHA256 via `signer.py`
- Keys from env via Pydantic-settings
- Rate limit: 20 req/sec REST
- Redis for: market cache (TTL 1–60s), order state, distributed locks, WS state
- Redis async; keys: `mexc:{entity}:{id}`
- Validate all external API responses via Pydantic

---

## 6. Cloud Deployment

- Cloud Run: multi-stage Docker, port 8080, `/health`, resource limits
- Scheduler: POST to Cloud Run, service account auth, retry policies
- Jobs: batch ops, idempotent, log executions

Env vars via Secret Manager:

```
MEXC_API_KEY, MEXC_API_SECRET, REDIS_URL, REDIS_PASSWORD, ENV=production, LOG_LEVEL=INFO
```

---

## 7. Do / Don't

**DO:** repo pattern, input validation, async I/O, circuit breakers, structured logging, Redis caching, graceful WS shutdown.
**DON’T:** direct Redis/MEXC in routes, encode business rules in routes/repos, sync I/O in async, time.sleep(), commit secrets, circular deps, mutable defaults.

---

## 8. Errors & Logging

- Result pattern for failures
- Custom exceptions in `core/exceptions.py`
- Log context: request_id, user_id, symbol, order_id
- Structured JSON logs; critical errors trigger alerts

Example:

```python
T, E = TypeVar("T"), TypeVar("E", bound=Exception)
@dataclass
class Ok(Generic[T]): value: T
@dataclass
class Err(Generic[E]): error: E
Result = Union[Ok[T], Err[E]]
```

---

## 9. Testing

- Unit: domain (mock deps)
- Integration: API (TestClient)
- pytest-asyncio, mock Redis + MEXC
- Fixtures in `tests/conftest.py`
- ≥80% domain coverage
- httpx.MockTransport for HTTP mocking

---

## 10. Perf & Cost

- Aggressive Redis caching
- Batch API calls
- WS for real-time data
- Proper TTL, connection pooling, request coalescing
- Monitor Cloud Run instances, set max

---

## 11. Output Expectations

- Prefer architectural explanation before code
- State assumptions/trade-offs
- Ask before non-trivial architectural changes
- No large code blocks unless requested
- Provide deployment commands

---

## 12. Style Enforcement

```toml
[tool.black]
line-length = 100
target-version = ['py311']
[tool.ruff]
line-length = 100
select = ["E","F","I","N","W","UP","B","A","C4","DTZ","T10","ISC","ICN","PIE","PT","Q","SIM","ARG","ERA","PD","PL","NPY","RUF"]
[tool.pytest.ini_options]
asyncio_mode="auto"
testpaths=["tests"]
```
