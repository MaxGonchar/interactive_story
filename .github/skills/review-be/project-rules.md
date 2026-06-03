# Backend Python Code Review Rules

This file is referenced by SKILL.md. Apply every rule in every section to each file under review.

---

## Section 1 — General Python Bad Practices

### 1.1 Mutable default arguments
**Pattern**: `def f(x=[])` or `def f(d={})` or `def f(s=set())`  
**Severity**: blocking  
**Why**: the default object is created once at function definition time and shared across all calls. Mutations persist between calls.  
**Fix**: use `None` as the default and assign inside the function body.

### 1.2 Bare `except` or catching `Exception` too broadly
**Pattern**: `except:` with no type, or `except Exception:` swallowing all errors silently (e.g. `pass` or only `logging`)  
**Severity**: warning  
**Why**: hides bugs, makes debugging hard, can catch `KeyboardInterrupt` and `SystemExit`.  
**Fix**: catch the narrowest exception type that applies. Re-raise if you cannot handle it.

### 1.3 Comparing with `== None` or `== True` / `== False`
**Pattern**: `if x == None:`, `if x == True:`  
**Severity**: note  
**Why**: `None`, `True`, and `False` are singletons; identity checks (`is`, `is not`) are correct and conventional.  
**Fix**: `if x is None:`, `if x:`, `if not x:`

### 1.4 Using `type(x) == SomeType` instead of `isinstance`
**Pattern**: `type(x) == int`  
**Severity**: note  
**Why**: `isinstance` respects inheritance; `type()` does not.  
**Fix**: `isinstance(x, int)`

### 1.5 String concatenation in a loop
**Pattern**: `result = ""; for ...: result += ...`  
**Severity**: warning  
**Why**: O(n²) string copies in CPython when strings are large.  
**Fix**: accumulate in a list and use `"".join(parts)`.

### 1.6 Returning `None` explicitly when the function always returns `None`
**Pattern**: `return None` at the end of a function that has no other return values  
**Severity**: note  
**Why**: redundant; Python already returns `None` implicitly.  
**Fix**: remove the `return None`.

### 1.7 Magic numbers and unexplained constants
**Pattern**: numeric literals in logic (e.g. `if len(msg) > 4000:`) with no named constant or comment  
**Severity**: note  
**Why**: intent is unclear to the next reader; changing the value requires hunting all occurrences.  
**Fix**: extract to a named constant at the module or class level.

### 1.8 Deeply nested code (arrow anti-pattern)
**Pattern**: more than 3 levels of indentation in a single block  
**Severity**: warning  
**Why**: hard to read and test; usually indicates missing early returns or extracted helpers.  
**Fix**: invert conditions for early returns, or extract inner blocks to helper functions.

### 1.9 Functions longer than ~40 lines
**Pattern**: function body exceeds ~40 lines (use judgment — some are fine)  
**Severity**: note  
**Why**: usually a sign of mixed responsibilities; harder to unit-test.  
**Fix**: extract cohesive sub-steps into private helpers.

### 1.10 Unused imports and variables
**Pattern**: `import X` where `X` never appears in the file body; variable assigned but never read  
**Severity**: note  
**Why**: clutters the file; can confuse readers about intent.  
**Fix**: remove them.

### 1.11 `print()` statements in non-utility code
**Pattern**: `print(...)` in services, repositories, or routers  
**Severity**: warning  
**Why**: debug artifacts left in production paths; use `logging` instead.  
**Fix**: replace with `logging.debug/info/warning/error`.

### 1.12 `assert` for runtime validation
**Pattern**: `assert condition, "message"` in non-test code  
**Severity**: blocking  
**Why**: assertions are disabled when Python runs with `-O`. They must not be used for input validation.  
**Fix**: raise an explicit exception (`ValueError`, `RuntimeError`, etc.).

---

## Section 2 — Async Correctness

### 2.1 Sequential `await` calls on independent coroutines
**Pattern**:
```python
a = await service_a.get(...)
b = await service_b.get(...)   # b does not depend on a
```
**Severity**: warning  
**Why**: each `await` suspends the coroutine until the result arrives. If the calls are independent, they can run concurrently with `asyncio.gather()`, cutting total latency.  
**Fix**:
```python
a, b = await asyncio.gather(service_a.get(...), service_b.get(...))
```
**How to detect**: look for two or more consecutive top-level `await` statements in an async function where the second call does not use the return value of the first.

### 2.2 Blocking I/O inside an async function
**Pattern**: `open(...)`, `yaml.safe_load(...)`, `time.sleep(...)`, `requests.get(...)` called directly (not via `asyncio.to_thread` or an async library) inside an `async def`  
**Severity**: blocking  
**Why**: blocks the entire event loop; no other coroutine can run while the blocking call is in progress.  
**Fix**: wrap in `await asyncio.to_thread(blocking_fn, ...)` or replace with an async equivalent (e.g. `aiofiles`).

### 2.3 Calling `asyncio.run()` inside an async context
**Pattern**: `asyncio.run(coro())` inside an `async def`  
**Severity**: blocking  
**Why**: raises `RuntimeError` — an event loop is already running.  
**Fix**: `await coro()` directly, or use `asyncio.create_task()` if fire-and-forget is needed.

### 2.4 Fire-and-forget tasks with no error handling
**Pattern**: `asyncio.create_task(coro())` with no `.add_done_callback` or awaiting  
**Severity**: warning  
**Why**: exceptions in detached tasks are silently swallowed unless a callback is attached.  
**Fix**: attach a done callback that logs or re-raises, or await the task before the function returns.

---

## Section 3 — Single Responsibility

### 3.1 Service accessing file system or YAML directly
**Pattern**: any `import yaml`, `open(...)`, `Path(...)` read/write, or `yaml_storage` call inside `app/services/*.py`  
**Severity**: blocking  
**Why**: per `progect_structure.md`, services must work with domain objects through repositories only. File access in a service bypasses the storage abstraction and makes unit testing without real files impossible.  
**Fix**: move the file access to the appropriate repository method; inject the repository.

### 3.2 Router containing business logic
**Pattern**: logic beyond: parse request → call service → map exceptions → return response, found in `app/api/routers/*.py`  
This includes: branching on domain state, constructing domain objects, calling repositories directly, or building LLM context.  
**Severity**: blocking  
**Why**: routers are HTTP glue; business logic there cannot be tested without HTTP.  
**Fix**: extract the logic to the appropriate service.

### 3.3 Repository containing business logic
**Pattern**: conditional branching on domain state (e.g. `if scene.finished:`) or orchestration of multiple storage operations that represent a business rule, found in `app/repositories/*.py`  
**Severity**: warning  
**Why**: repositories must only translate between domain objects and storage; domain rules belong in services.  
**Fix**: move the rule to the calling service.

### 3.4 LLM client responsible for prompt construction
**Pattern**: in `app/llm/scene_llm_client.py` — assembling the system prompt or building LangChain message lists inline rather than delegating to `PromptBuilder`  
**Severity**: warning  
**Why**: per `progect_structure.md` and `plan.md`, `SceneLLMClient` should call the LLM with a prepared context; `PromptBuilder` owns the prompt shape. Mixing both in the client makes either hard to test or change independently.  
**Fix**: ensure `SceneLLMClient.invoke()` only calls `self._prompt_builder.build_*()` and `self._model.ainvoke()`. All message assembly belongs in `PromptBuilder`.

### 3.5 Class or function with more than one distinct purpose
**Pattern**: a class with methods that serve clearly different concerns (e.g. a service that both queries data and mutates state with no clear aggregation reason), or a function doing I/O, transformation, and business validation all in one body  
**Severity**: warning  
**Why**: violates SRP; changes to one concern require touching code owned by the other.  
**Fix**: split into two classes or functions along the responsibility boundary.

---

## Section 4 — Dependency Injection

### 4.1 Service or repository constructing its own dependencies
**Pattern**: `self._repo = SceneRepository()` or `self._client = SceneLLMClient()` inside `__init__` without receiving them as constructor parameters  
**Severity**: blocking  
**Why**: creates a hidden, untestable hard-wiring. Unit tests cannot substitute a mock without monkey-patching.  
**Fix**: accept all dependencies as constructor parameters. Wire them in `app/api/dependencies.py`.

### 4.2 Hard-coded path or config value inside a class
**Pattern**: path strings like `"data/stories"` or `os.environ["KEY"]` read directly inside a service or repository `__init__` or method, rather than being injected  
**Severity**: warning  
**Why**: makes the class non-portable and untestable without real files or environment variables.  
**Fix**: inject the path/config as a constructor parameter or read it once in `dependencies.py` and pass it in.

### 4.3 Missing factory function in `dependencies.py`
**Pattern**: a service or repository that is used in a router but has no corresponding `get_*` factory in `app/api/dependencies.py`  
**Severity**: warning  
**Why**: the DI wiring is incomplete; FastAPI will not be able to inject it, or it will be instantiated ad-hoc inside the router (violating 4.1).  
**Fix**: add a `get_<service_name>()` function to `dependencies.py` that constructs and returns the dependency with its own dependencies injected.

### 4.4 Global mutable state used as a substitute for DI
**Pattern**: module-level mutable variables (not constants) read or written by multiple classes or functions as shared state  
**Severity**: blocking  
**Why**: race conditions in async code; makes execution order-dependent; untestable in isolation.  
**Fix**: pass state explicitly through constructors or function parameters.

---

## Section 5 — Project-Specific Conventions

These rules are derived from `docks/dev/progect_structure.md`, `docks/dev/plan.md`, and `docks/dev/data_storage_structure.md`.

### 5.1 Repository write not using `atomic_write`
**Pattern**: any write to a YAML file in `app/repositories/*.py` that does NOT use the `atomic_write` utility (i.e. `open(..., "w")` directly or `yaml_storage.write` without the atomic wrapper)  
**Severity**: blocking  
**Why**: per M4 exit criteria, all write operations must be atomic to prevent partial writes on crash.  
**Fix**: use `atomic_write` from `app/utils/atomic_write.py`.

### 5.2 Repository returning raw dicts instead of domain objects
**Pattern**: a repository method returning `dict`, `list[dict]`, or raw YAML-parsed data instead of a typed domain model from `app/models/domain.py` or `app/models/storage.py`  
**Severity**: blocking  
**Why**: per M4 exit criteria and the Repository pattern, repositories must translate storage format → domain model.  
**Fix**: map the raw dict to the appropriate `@dataclass` or Pydantic model before returning.

### 5.3 API error mapping inconsistency
**Pattern**: in `app/api/routers/*.py` — a `KeyError` mapped to anything other than 404, or a `ValueError` mapped to anything other than 409; or exceptions from services/repos not caught at all in the router  
**Severity**: warning  
**Why**: the project has an established contract (`KeyError`→404, `ValueError`→409). Deviating creates inconsistent API behavior.  
**Fix**: align the `except` blocks to the established mapping. Add missing handlers.

### 5.4 LangChain used beyond templating and invocation
**Pattern**: in `app/llm/` — use of LangChain agents, tools, multi-step chains (`SequentialChain`, `LLMChain` with branching), or any autonomous planning abstraction  
**Severity**: warning  
**Why**: per `progect_structure.md`, LangChain is scoped to prompt templating + model invocation only for MVP.  
**Fix**: replace with direct `SystemMessage`/`HumanMessage`/`AIMessage` construction and `model.ainvoke()`.

### 5.5 `context_data` not populated before LLM call
**Pattern**: in `app/services/scene_play_service.py` — `SceneContext` constructed with `context_data` absent or always empty, without querying prior scene summaries from `StoryRepository`  
**Severity**: warning  
**Why**: per the system prompt correction issue in `plan.md`, the LLM needs prior scene summaries as narrative background. Leaving `context_data=[]` always produces a context-free response.  
**Fix**: fetch `story_meta.scenes[*].summary` for finished scenes preceding the current one and pass them as `context_data`.

### 5.6 Message history not forwarded to LLM
**Pattern**: in `app/llm/scene_llm_client.py` — `context.messages` is not converted to LangChain message objects (`AIMessage`/`HumanMessage`) and inserted between the `SystemMessage` and the current `HumanMessage`  
**Severity**: blocking  
**Why**: the LLM has no conversational memory within a scene — every reply is generated without knowledge of prior turns.  
**Fix**: build the full message chain: `[SystemMessage] + [history...] + [HumanMessage(current)]`.

### 5.7 Console stubs left in production handlers
**Pattern**: `console.log(...)` or `print(...)` as the only body of an event handler or service method (i.e. a stub that was never replaced with real logic)  
**Severity**: blocking  
**Why**: features silently do nothing. Per `plan.md`'s known issues, several handlers were stubs from M3 that survived into M6.  
**Fix**: implement the real logic or raise `NotImplementedError` with a clear message.
