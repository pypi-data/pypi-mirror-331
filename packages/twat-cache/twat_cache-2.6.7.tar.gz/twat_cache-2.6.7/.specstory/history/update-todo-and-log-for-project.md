## SpecStory

## Update TODO and LOG for Project (16/02/2025, 06:57:40)

_**User**_

Read @T@TODO.md ODO.md from 2.1.4. onwards. Rewrite that section, mark what's done, update @LOG.md 

As you develop, run 

```
uv venv; source .venv/bin/activate; uv pip install -e .[all,dev,test]; hatch run lint:fix; hatch test;
```

then continue on what's still TODO


---

_**Assistant**_

Let me help you update the TODO list and LOG based on the current state. First, I'll check the project status.

---

_****_

```bash
uv venv; source .venv/bin/activate; uv pip install -e .[all,dev,test]; hatch run lint:fix; hatch test
```

```
Using CPython 3.12.8 interpreter at: /usr/local/bin/python3.12
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
zsh: no matches found: .[all,dev,test]
warning: The top-level linter settings are deprecated in favour of their c
ounterparts in the `lint` section. Please update the following options in `pypro
ject.toml`:                                                           - 'per-fil
e-ignores' -> 'lint.per-file-ignores'
src/twat_cache/config.py:165:26: PLR2004 Magic value used in comparison, c
onsider replacing `9` with a constant variable                                |
163 |     def validate_compression_level(self, v: int) -> int:
164 |         """Validate compression level."""
165 |         if not 1 <= v <= 9:
    |                          ^ PLR2004
166 |             msg = "compression_level must be between 1 and 9"
167 |             raise ValueError(msg)
    |

src/twat_cache/config.py:222:30: T201 `print` found
    |
220 |         level = "DEBUG" if self.debug else "INFO"
221 |         logger.add(
222 |             sink=lambda msg: print(msg, end=""),
    |                              ^^^^^ T201
223 |             level=level,
224 |             format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    |
    = help: Remove `print`

src/twat_cache/decorators.py:19:5: FBT001 Boolean-typed positional argumen
t in function definition                                                     |
17 |     maxsize: int | None = None,
18 |     folder_name: str | None = None,
19 |     use_sql: bool = False,
   |     ^^^^^^^ FBT001
20 |     preferred_engine: str | None = None,
21 |     cache_type: str | None = None,
   |

src/twat_cache/decorators.py:19:5: FBT002 Boolean default positional argum
ent in function definition                                                   |
17 |     maxsize: int | None = None,
18 |     folder_name: str | None = None,
19 |     use_sql: bool = False,
   |     ^^^^^^^ FBT002
20 |     preferred_engine: str | None = None,
21 |     cache_type: str | None = None,
   |

src/twat_cache/engines/functools.py:1:1: A005 Module `functools` shadows a
 Python standard-library module                                           src/tw
at_cache/engines/joblib.py:49:33: ARG002 Unused method argument: `ke
y`                                                                           |
47 |         )
48 |
49 |     def _get_cached_value(self, key: CacheKey) -> R | None:
   |                                 ^^^ ARG002
50 |         """Retrieve a value from the cache.
   |

src/twat_cache/engines/klepto.py:20:34: ARG005 Unused lambda argument: `ar
gs`                                                                          |
18 |     HAS_KLEPTO = False
19 |     dir_archive = type("dir_archive", (), {})  # type: ignore
20 |     keymap = picklemap = lambda *args, **kwargs: lambda f: f  # type:
 ignore                                                                      |
                                ^^^^ ARG005
   |

src/twat_cache/engines/klepto.py:20:42: ARG005 Unused lambda argument: `kw
args`                                                                        |
18 |     HAS_KLEPTO = False
19 |     dir_archive = type("dir_archive", (), {})  # type: ignore
20 |     keymap = picklemap = lambda *args, **kwargs: lambda f: f  # type:
 ignore                                                                      |
                                        ^^^^^^ ARG005
   |

src/twat_cache/paths.py:100:5: C901 `clear_cache` is too complex (11 > 10)
    |
100 | def clear_cache(folder_name: str | None = None) -> None:
    |     ^^^^^^^^^^^ C901
101 |     """
102 |     Clear the cache directory for the given folder name.
    |

src/twat_cache/types.py:1:1: A005 Module `types` shadows a Python standard
-library module                                                           tests/
test_cache.py:20:7: F811 Redefinition of unused `CacheConfig` from l
ine 17                                                                       |
20 | class CacheConfig(TypedDict, total=False):
   |       ^^^^^^^^^^^ F811
21 |     """Type definition for cache configuration."""
   |
   = help: Remove definition: `CacheConfig`

tests/test_cache.py:185:34: PLR2004 Magic value used in comparison, consid
er replacing `15` with a constant variable                                    |
183 |     result2 = process_list(test_list)
184 |
185 |     assert result1 == result2 == 15
    |                                  ^^ PLR2004
    |

tests/test_config.py:114:38: PLR2004 Magic value used in comparison, consi
der replacing `500` with a constant variable                                  |
113 |     # Check values
114 |     assert config.default_maxsize == 500
    |                                      ^^^ PLR2004
115 |     assert config.default_use_sql is True
116 |     assert config.default_engine == "disk"
    |

tests/test_config.py:135:36: PLR2004 Magic value used in comparison, consi
der replacing `200` with a constant variable                                  |
133 |         folder_name="test_cache",
134 |     )
135 |     assert cache_config.maxsize == 200
    |                                    ^^^ PLR2004
136 |     assert cache_config.folder_name == "test_cache"
137 |     assert cache_config.use_sql == global_config.default_use_sql
    |

tests/test_config.py:147:36: PLR2004 Magic value used in comparison, consi
der replacing `300` with a constant variable                                  |
145 |         preferred_engine="disk",
146 |     )
147 |     assert cache_config.maxsize == 300
    |                                    ^^^ PLR2004
148 |     assert cache_config.folder_name == "custom_cache"
149 |     assert cache_config.use_sql is True
    |

tests/test_engines.py:145:28: PLR2004 Magic value used in comparison, cons
ider replacing `10` with a constant variable                                  |
144 |     # First call should compute
145 |     assert test_func(5) == 10
    |                            ^^ PLR2004
146 |     assert call_count == 1
147 |     assert test_engine.stats["hits"] == 0
    |

tests/test_engines.py:151:28: PLR2004 Magic value used in comparison, cons
ider replacing `10` with a constant variable                                  |
150 |     # Second call should use cache
151 |     assert test_func(5) == 10
    |                            ^^ PLR2004
152 |     assert call_count == 1
153 |     assert test_engine.stats["hits"] == 1
    |

tests/test_engines.py:157:29: PLR2004 Magic value used in comparison, cons
ider replacing `20` with a constant variable                                  |
156 |     # Different arg should compute
157 |     assert test_func(10) == 20
    |                             ^^ PLR2004
158 |     assert call_count == 2
159 |     assert test_engine.stats["hits"] == 1
    |

tests/test_engines.py:158:26: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
156 |     # Different arg should compute
157 |     assert test_func(10) == 20
158 |     assert call_count == 2
    |                          ^ PLR2004
159 |     assert test_engine.stats["hits"] == 1
160 |     assert test_engine.stats["misses"] == 2
    |

tests/test_engines.py:160:43: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
158 |     assert call_count == 2
159 |     assert test_engine.stats["hits"] == 1
160 |     assert test_engine.stats["misses"] == 2
    |                                           ^ PLR2004
    |

tests/test_engines.py:190:38: PLR2004 Magic value used in comparison, cons
ider replacing `10` with a constant variable                                  |
188 |         lru_engine._set_cached_value(("key", i), i)
189 |
190 |     assert len(lru_engine._cache) == 10
    |                                      ^^ PLR2004
191 |
192 |     # Add one more, should evict oldest
    |

tests/test_engines.py:194:38: PLR2004 Magic value used in comparison, cons
ider replacing `10` with a constant variable                                  |
192 |     # Add one more, should evict oldest
193 |     lru_engine._set_cached_value(("key", 10), 10)
194 |     assert len(lru_engine._cache) == 10
    |                                      ^^ PLR2004
195 |     assert ("key", 0) not in lru_engine._cache  # First item should 
be evicted                                                                196 |
    assert ("key", 10) in lru_engine._cache  # New item should be pr
esent                                                                         |

tests/test_engines.py:205:38: PLR2004 Magic value used in comparison, cons
ider replacing `5` with a constant variable                                   |
203 |         lru_engine._set_cached_value(("key", i), i)
204 |
205 |     assert len(lru_engine._cache) == 5
    |                                      ^ PLR2004
206 |
207 |     # Clear cache
    |

tests/test_engines.py:248:29: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
247 |     stats = lru_engine.stats
248 |     assert stats["hits"] == 2
    |                             ^ PLR2004
249 |     assert stats["misses"] == 2
250 |     assert stats["size"] == 2
    |

tests/test_engines.py:249:31: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
247 |     stats = lru_engine.stats
248 |     assert stats["hits"] == 2
249 |     assert stats["misses"] == 2
    |                               ^ PLR2004
250 |     assert stats["size"] == 2
251 |     assert stats["current_size"] == 2
    |

tests/test_engines.py:250:29: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
248 |     assert stats["hits"] == 2
249 |     assert stats["misses"] == 2
250 |     assert stats["size"] == 2
    |                             ^ PLR2004
251 |     assert stats["current_size"] == 2
    |

tests/test_engines.py:251:37: PLR2004 Magic value used in comparison, cons
ider replacing `2` with a constant variable                                   |
249 |     assert stats["misses"] == 2
250 |     assert stats["size"] == 2
251 |     assert stats["current_size"] == 2
    |                                     ^ PLR2004
    |

Found 37 errors (10 fixed, 27 remaining).
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1xkE/hatch-test.p
y3.12/bin/python3                                                   cachedir: .p
ytest_cache
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache                                            config
file: pyproject.toml
plugins: rerunfailures-14.0, mock-3.14.0, xdist-3.6.1
collected 0 items / 4 errors                                             

================================= ERRORS =================================
__________________ ERROR collecting tests/test_cache.py __________________
tests/test_cache.py:15: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel, CacheConfigBase):
src/twat_cache/config.py:67: in CacheConfig
    @field_validator("maxsize")
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/hatch-test.py3.12/lib/python3.12/site-packages/pydantic/functional_validator
s.py:501: in dec                                                        raise Py
danticUserError(
E   pydantic.errors.PydanticUserError: `@field_validator` cannot be applie
d to instance methods                                                     E   
E   For further information visit https://errors.pydantic.dev/2.10/u/valid
ator-instance-method                                                      ______
___________ ERROR collecting tests/test_config.py __________________
tests/test_config.py:19: in <module>
    from twat_cache.config import CacheConfig, GlobalConfig
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel, CacheConfigBase):
src/twat_cache/config.py:67: in CacheConfig
    @field_validator("maxsize")
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/hatch-test.py3.12/lib/python3.12/site-packages/pydantic/functional_validator
s.py:501: in dec                                                        raise Py
danticUserError(
E   pydantic.errors.PydanticUserError: `@field_validator` cannot be applie
d to instance methods                                                     E   
E   For further information visit https://errors.pydantic.dev/2.10/u/valid
ator-instance-method                                                      ______
___________ ERROR collecting tests/test_engines.py _________________
tests/test_engines.py:24: in <module>
    from twat_cache.engines.base import BaseCacheEngine
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel, CacheConfigBase):
src/twat_cache/config.py:67: in CacheConfig
    @field_validator("maxsize")
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/hatch-test.py3.12/lib/python3.12/site-packages/pydantic/functional_validator
s.py:501: in dec                                                        raise Py
danticUserError(
E   pydantic.errors.PydanticUserError: `@field_validator` cannot be applie
d to instance methods                                                     E   
E   For further information visit https://errors.pydantic.dev/2.10/u/valid
ator-instance-method                                                      ______
_________ ERROR collecting tests/test_twat_cache.py ________________
tests/test_twat_cache.py:20: in <module>
    from twat_cache.engines.functools import FunctoolsCacheEngine
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel, CacheConfigBase):
src/twat_cache/config.py:67: in CacheConfig
    @field_validator("maxsize")
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/hatch-test.py3.12/lib/python3.12/site-packages/pydantic/functional_validator
s.py:501: in dec                                                        raise Py
danticUserError(
E   pydantic.errors.PydanticUserError: `@field_validator` cannot be applie
d to instance methods                                                     E   
E   For further information visit https://errors.pydantic.dev/2.10/u/valid
ator-instance-method                                                      ======
================== short test summary info =========================
ERROR tests/test_cache.py - pydantic.errors.PydanticUserError: `@field_val
idator` cannot be appli...                                                ERROR
tests/test_config.py - pydantic.errors.PydanticUserError: `@field_va
lidator` cannot be appli...                                               ERROR
tests/test_engines.py - pydantic.errors.PydanticUserError: `@field_v
alidator` cannot be appli...                                              ERROR
tests/test_twat_cache.py - pydantic.errors.PydanticUserError: `@fiel
d_validator` cannot be appli...                                           !!!!!!
!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!
=========================== 4 errors in 0.37s ============================

```

---

_****_



I see there are some issues with the tests and linting that need to be addressed. Let me first update the TODO.md and LOG.md with the current status and then we can work on fixing these issues.

---

_****_

```diff
    + ✅ **2.1.4.** Remove custom SQL and Redis implementations.
    + **2.1.5.** Fix failing tests and complete test coverage:
-     - ✅ Fix CacheConfig instantiation issues
+     - ❌ Fix Pydantic field validator issues in CacheConfig
+     - ❌ Fix linting issues (27 remaining)
      - ❌ Fix cache stats tracking
      - ❌ Fix list/unhashable type handling
      - ❌ Fix cache clearing behavior
-     - **2.1.6.** Add missing engine-specific tests:
-       - ❌ Test cache eviction policies
-       - ❌ Test concurrent access
-       - ❌ Test error handling
-       - ❌ Test serialization/deserialization
-       - ❌ Test memory limits
+   + **2.1.6.** Add missing engine-specific tests:
+     - ❌ Test cache eviction policies
+     - ❌ Test concurrent access
+     - ❌ Test error handling
+     - ❌ Test serialization/deserialization
+     - ❌ Test memory limits
+     - ❌ Test cache invalidation strategies
  
  * **2.2. Enhance `EngineManager`:**
      - ❌ Add tests for caching behavior
  
- * **2.3. Improve Type Hinting:**
-   + **2.3.1. Use `typing_extensions`:**
-     - ✅ Add to dependencies
+ * **2.3. Improve Type System:**
+   + **2.3.1. Pydantic Integration:**
+     - ❌ Fix field validator implementation
+     - ❌ Add proper model validation
+     - ❌ Add custom error messages
+   + **2.3.2. Type Hints:**
+     - ✅ Use `typing_extensions`
      - ✅ Update type imports
-   + **2.3.2. Generic Types:**
-     - ✅ Fix type variable usage
-     - ✅ Add proper constraints
+     - ❌ Add proper generic constraints
    + **2.3.3. Type Stubs:**
      - ❌ Create stub directory
      - ❌ Add stubs for optional backends
+     - ❌ Add type tests
  
- * **2.4. Configuration and Defaults:**
-   + **2.4.1. Centralized Configuration:**
-     - ✅ Fix CacheConfig implementation
-     - ✅ Update engine constructors
-     - ✅ Remove redundant parameters
+ * **2.4. Configuration System:**
+   + **2.4.1. Validation:**
+     - ❌ Fix Pydantic model validation
+     - ❌ Add config schema validation
+     - ❌ Add runtime checks
    + **2.4.2. Environment Variables:**
+     - ❌ Add env var support
      - ❌ Document in README.md
      - ❌ Add validation
    + **2.4.3. Default Values:**
      - ✅ Review and update
      - ✅ Add documentation
+     - ❌ Add validation tests
  
  * **2.5. `ucache` Decorator Refinement:**
```

---

_****_



Now let me update the LOG.md with our current status and next steps.

---

_****_

```diff
     - Add migration guide for users of removed implementations
  
+ ### 2024-03-19
+ #### Current Status
+ - Ran development setup and tests
+ - Found critical issues that need immediate attention:
+   1. Pydantic field validator errors in CacheConfig
+   2. 27 remaining linting issues
+   3. Test failures across all test files
+ 
+ #### Critical Issues
+ 
+ 1. **Pydantic Integration Issues**
+    - Error: `@field_validator` cannot be applied to instance methods
+    - Location: `src/twat_cache/config.py`
+    - Impact: Breaking all tests due to config initialization failure
+ 
+ 2. **Linting Issues**
+    - 27 remaining issues including:
+      - Magic numbers in comparisons
+      - Print statements in production code
+      - Boolean positional arguments
+      - Module naming conflicts
+      - Complex function warnings
+ 
+ #### Next Steps
+ 
+ 1. **Immediate Fixes**
+    - Fix Pydantic field validator implementation in CacheConfig
+    - Address critical linting issues affecting functionality
+    - Fix test failures
+ 
+ 2. **Short-term Tasks**
+    - Complete cache stats tracking implementation
+    - Add proper type constraints
+    - Implement missing test cases
+ 
+ 3. **Documentation Updates**
+    - Document configuration system
+    - Add validation rules
+    - Update type hints documentation
+ 
  
```

---

_****_



Let's start by fixing the most critical issue - the Pydantic field validator error. I'll examine the config file first.

---

_****_

Read file: src/twat_cache/config.py

---

_****_



I see the issue. In Pydantic v2, `@field_validator` is a class method decorator, but we're using it as an instance method. Let me fix this by updating the validators to be class methods.

---

_****_

```diff
      }
  
+     @classmethod
      @field_validator("maxsize")
-     def validate_maxsize(self, v: int | None) -> int | None:
+     def validate_maxsize(cls, v: int | None) -> int | None:
          """Validate maxsize setting."""
          if v is not None and v <= 0:
          return v
  
+     @classmethod
      @field_validator("folder_name")
-     def validate_folder_name(self, v: str | None) -> str | None:
+     def validate_folder_name(cls, v: str | None) -> str | None:
          """Validate folder name setting."""
          if v is not None and not v.strip():
          return v
  
+     @classmethod
      @field_validator("cache_type")
-     def validate_cache_type(self, v: CacheType | None) -> CacheType | None:
+     def validate_cache_type(cls, v: CacheType | None) -> CacheType | None:
          """Validate cache type setting."""
          valid_types = {"speed", "database", "filesystem", None}
      )
  
+     @classmethod
      @field_validator("compression_level")
-     def validate_compression_level(self, v: int) -> int:
+     def validate_compression_level(cls, v: int) -> int:
          """Validate compression level."""
          if not 1 <= v <= 9:
          return v
  
+     @classmethod
      @field_validator("log_file")
-     def validate_log_file(self, v: Path | None | str) -> Path | None:
-         """Convert string log file path to Path object."""
+     def validate_log_file(cls, v: Path | None | str) -> Path | None:
+         """Validate log file path."""
          if v is None:
              return None
          if isinstance(v, str):
-             return Path(v)
+             v = Path(v)
+         if not v.parent.exists():
+             v.parent.mkdir(parents=True, exist_ok=True)
          return v
  
```

---

_****_



Now let's run the tests again to see if this fixed the Pydantic validator issues.

---

_****_

```bash
hatch run test
```

```
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pytest_asyncio/plugin.py:207:
PytestDeprecationWarning: The configuration option "asyncio_default_fixtur
e_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture
 caching scope. Future versions of pytest-asyncio will default the loop sc
ope for asynchronous fixtures to function scope. Set the default fixture l
oop scope explicitly in order to avoid unexpected behavior in the future.
Valid fixture loop scopes are: "function", "class", "module", "package", "
session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET
))
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1xkE/twat-c
ache/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_r
ounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=Fal
se warmup_iterations=100000)
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache
configfile: pyproject.toml
plugins: cov-6.0.0, asyncio-0.25.3, benchmark-5.1.0, xdist-3.6.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None
collected 57 items                                                       

tests/test_cache.py::test_cache_settings_validation FAILED         [  1%]
tests/test_cache.py::test_basic_caching PASSED                     [  3%]
tests/test_cache.py::test_cache_clear FAILED                       [  5%]
tests/test_cache.py::test_cache_stats FAILED                       [  7%]
tests/test_cache.py::test_list_processing PASSED                   [  8%]
tests/test_cache.py::test_different_backends PASSED                [ 10%]
tests/test_cache.py::test_cache_with_complex_types PASSED          [ 12%]
tests/test_cache.py::test_cache_exceptions FAILED                  [ 14%]
tests/test_cache.py::test_kwargs_handling FAILED                   [ 15%]
tests/test_config.py::test_cache_config_validation FAILED          [ 17%]
tests/test_config.py::test_default_config FAILED                   [ 19%]
tests/test_config.py::test_custom_config FAILED                    [ 21%]
tests/test_config.py::test_global_config_env_vars PASSED           [ 22%]
tests/test_config.py::test_get_cache_config FAILED                 [ 24%]
tests/test_config.py::test_logging_configuration PASSED            [ 26%]
tests/test_config.py::test_cache_config_creation FAILED            [ 28%]
tests/test_config.py::test_cache_config_with_sql FAILED            [ 29%]
tests/test_engines.py::test_base_engine_initialization ERROR       [ 31%]
tests/test_engines.py::test_base_engine_key_generation PASSED      [ 33%]
tests/test_engines.py::test_base_engine_cache_decorator PASSED     [ 35%]
tests/test_engines.py::test_base_engine_validation ERROR           [ 36%]
tests/test_engines.py::test_lru_cache_initialization ERROR         [ 38%]
tests/test_engines.py::test_lru_cache_maxsize_enforcement FAILED   [ 40%]
tests/test_engines.py::test_lru_cache_clear PASSED                 [ 42%]
tests/test_engines.py::test_lru_cache_with_complex_values PASSED   [ 43%]
tests/test_engines.py::test_lru_cache_stats_accuracy PASSED        [ 45%]
tests/test_engines.py::test_engine_registration FAILED             [ 47%]
tests/test_engines.py::test_engine_selection FAILED                [ 49%]
tests/test_engines.py::test_invalid_engine_registration PASSED     [ 50%]
tests/test_engines.py::test_engine_manager_singleton PASSED        [ 52%]
tests/test_engines.py::test_engine_configuration FAILED            [ 54%]
tests/test_engines.py::test_unavailable_engine FAILED              [ 56%]
tests/test_engines.py::test_engine_stats PASSED                    [ 57%]
tests/test_engines.py::test_engine_clear ERROR                     [ 59%]
tests/test_engines.py::test_engine_caching FAILED                  [ 61%]
tests/test_engines.py::test_lru_maxsize FAILED                     [ 63%]
tests/test_engines.py::test_lru_clear PASSED                       [ 64%]
tests/test_engines.py::test_lru_stats FAILED                       [ 66%]
tests/test_engines.py::test_functools_cache_maxsize_enforcement PASSED [ 6
8%]
tests/test_engines.py::test_functools_cache_clear PASSED           [ 70%]
tests/test_engines.py::test_functools_cache_with_complex_values PASSED [ 7
1%]
tests/test_engines.py::test_functools_cache_stats_accuracy PASSED  [ 73%]
tests/test_engines.py::test_functools_maxsize PASSED               [ 75%]
tests/test_engines.py::test_functools_clear PASSED                 [ 77%]
tests/test_engines.py::test_functools_stats PASSED                 [ 78%]
tests/test_twat_cache.py::test_lru_cache_get_set ERROR             [ 80%]
tests/test_twat_cache.py::test_lru_cache_clear ERROR               [ 82%]
tests/test_twat_cache.py::test_lru_cache_maxsize ERROR             [ 84%]
tests/test_twat_cache.py::test_disk_cache_persistence ERROR        [ 85%]
tests/test_twat_cache.py::test_joblib_numpy_array ERROR            [ 87%]
tests/test_twat_cache.py::test_klepto_persistence ERROR            [ 89%]
tests/test_twat_cache.py::test_async_cache_operations ERROR        [ 91%]
tests/test_twat_cache.py::test_cachebox_operations ERROR           [ 92%]
tests/test_twat_cache.py::test_cachetools_operations ERROR         [ 94%]
tests/test_twat_cache.py::test_functools_cache_get_set ERROR       [ 96%]
tests/test_twat_cache.py::test_functools_cache_clear ERROR         [ 98%]
tests/test_twat_cache.py::test_functools_cache_maxsize ERROR       [100%]

================================= ERRORS =================================
___________ ERROR at setup of test_base_engine_initialization ____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 110
  def test_base_engine_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:110
_____________ ERROR at setup of test_base_engine_validation ______________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 163
  def test_base_engine_validation(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:163
____________ ERROR at setup of test_lru_cache_initialization _____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 176
  def test_lru_cache_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:176
__________________ ERROR at setup of test_engine_clear ___________________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 365
  def test_engine_clear(engine: BaseCacheEngine[Any, Any]) -> None:
E       fixture 'engine' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:365
________________ ERROR at setup of test_lru_cache_get_set ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_________________ ERROR at setup of test_lru_cache_clear _________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
________________ ERROR at setup of test_lru_cache_maxsize ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_disk_cache_persistence ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_joblib_numpy_array ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_klepto_persistence ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_async_cache_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_cachebox_operations _______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_cachetools_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_get_set _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_functools_cache_clear ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_maxsize _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
================================ FAILURES ================================
_____________________ test_cache_settings_validation _____________________

    def test_cache_settings_validation() -> None:
        """Test validation of cache settings."""
        # Valid settings
        config = CacheConfig(maxsize=100)
>       config.validate()  # Should not raise
E       AttributeError: 'dict' object has no attribute 'validate'

tests/test_cache.py:32: AttributeError
____________________________ test_cache_clear ____________________________

    def test_cache_clear() -> None:
        """Test cache clearing functionality."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # First call
        assert cached_function(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
    
        # Clear cache
        clear_cache()
    
        # Should recompute after clear
        assert cached_function(TEST_INPUT) == TEST_RESULT
>       assert call_count == EXPECTED_CALL_COUNT
E       assert 1 == 2

tests/test_cache.py:96: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.498 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
4d28a04a
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
6900760b
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.cache:clear_cache:55 - Cle
aring cache for engine: FunctoolsCacheEngine
2025-02-16 06:58:58.499 | DEBUG    | twat_cache.engines.functools:clear:12
9 - Cleared functools cache
____________________________ test_cache_stats ____________________________

    def test_cache_stats() -> None:
        """Test cache statistics."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # Generate some cache activity
        for _i in range(3):
            cached_function(TEST_INPUT)
            cached_function(TEST_INPUT_2)
    
        # Get stats
        stats = get_stats()
    
        # Basic stats checks
        assert isinstance(stats, dict)
>       assert stats["hits"] >= MIN_STATS_COUNT
E       assert 0 >= 2

tests/test_cache.py:119: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.504 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.504 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
7127190b
2025-02-16 06:58:58.504 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.504 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
cbd44fd1
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.505 | DEBUG    | twat_cache.cache:get_stats:93 - Getti
ng stats for engine: FunctoolsCacheEngine
_________________________ test_cache_exceptions __________________________

    def test_cache_exceptions() -> None:
        """Test caching of exceptions."""
        call_count = 0
    
        @ucache(maxsize=100)
        def failing_function(x: int) -> None:
            nonlocal call_count
            call_count += 1
            msg = "Test error"
            raise ValueError(msg)
    
        # First call
        with pytest.raises(ValueError):
            failing_function(5)
        assert call_count == 1
    
        # Second call should not recompute
        with pytest.raises(ValueError):
            failing_function(5)
>       assert call_count == 1
E       assert 2 == 1

tests/test_cache.py:207: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.516 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.516 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
855fbc4f
2025-02-16 06:58:58.516 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=100 folder_name=Non
e use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.516 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.516 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
__________________________ test_kwargs_handling __________________________

    def test_kwargs_handling() -> None:
        """Test caching with different keyword arguments."""
        call_count = 0
    
        @ucache()
        def kwarg_function(x: int, multiplier: int = 1) -> int:
            nonlocal call_count
            call_count += 1
            return x * multiplier
    
        # Test with different kwarg combinations
        assert kwarg_function(TEST_INPUT) == TEST_INPUT
        assert call_count == 1
    
        assert kwarg_function(TEST_INPUT, multiplier=1) == TEST_INPUT
>       assert call_count == 1  # Should use cache
E       assert 2 == 1

tests/test_cache.py:225: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.521 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 06:58:58.521 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
c94203e5
2025-02-16 06:58:58.521 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 06:58:58.521 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 06:58:58.521 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
______________________ test_cache_config_validation ______________________

    def test_cache_config_validation() -> None:
        """Test validation of cache configuration."""
        # Valid configurations
        config = CacheConfig(maxsize=100)
>       config.validate_maxsize()  # Should not raise
E       TypeError: CacheConfig.validate_maxsize() missing 1 required posit
ional argument: 'v'

tests/test_config.py:52: TypeError
__________________________ test_default_config ___________________________

    def test_default_config() -> None:
        """Test default configuration values."""
        config = GlobalConfig()
    
        # Check default values
>       assert config.cache_dir == get_cache_path()
E       AssertionError: assert PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_5571e959') == PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_a6a89a4b')
E        +  where PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_5571e959') = GlobalConfig(cache_dir=PosixPath('/Users/adam/Library/Cac
hes/twat_cache/twat_cache_5571e959'), default_maxsize=1000, default_use_sq
l=False, default_engine='lru', default_cache_type=None, enable_compression
=True, compression_level=6, debug=False, log_file=None).cache_dir
E        +  and   PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_a6a89a4b') = get_cache_path()

tests/test_config.py:72: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.532 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
5571e959
2025-02-16 06:58:58.532 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
a6a89a4b
___________________________ test_custom_config ___________________________

    def test_custom_config() -> None:
        """Test custom configuration values."""
        config = GlobalConfig(
            default_maxsize=CUSTOM_MAXSIZE,
            default_use_sql=True,
            default_engine="disk",
            enable_compression=False,
            debug=True,
            log_file="cache.log",
        )
    
        # Check values
>       assert config.default_maxsize == CUSTOM_MAXSIZE
E       AssertionError: assert 1000 == 500
E        +  where 1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_49ccdde7'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:94: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.538 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
49ccdde7
_________________________ test_get_cache_config __________________________

    def test_get_cache_config() -> None:
        """Test getting cache configuration with defaults."""
        global_config = GlobalConfig()
    
        # Test with no overrides
        cache_config = global_config.get_cache_config()
>       assert cache_config.maxsize == global_config.default_maxsize
E       AssertionError: assert None == 1000
E        +  where None = CacheConfig(maxsize=1000, folder_name=None, use_s
ql=False, preferred_engine='lru', cache_type=None).maxsize
E        +  and   1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_21383a51'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:126: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 06:58:58.548 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
21383a51
_______________________ test_cache_config_creation _______________________

    def test_cache_config_creation() -> None:
        """Test cache configuration creation."""
        global_config = GlobalConfig()
    
        # Create cache config with some overrides
        cache_config = CacheConfig(
            maxsize=CACHE_CONFIG_MAXSIZE,
            folder_name="test_cache",
        )
    
>       assert cache_config.maxsize == CACHE_CONFIG_MAXSIZE
E       AssertionError: assert None == 200
E        +  where None = CacheConfig(maxsize=200, folder_name='test_cache'
, use_sql=False, preferred_engine=None, cache_type=None).maxsize

tests/test_config.py:183: AssertionError
_______________________ test_cache_config_with_sql _______________________

    def test_cache_config_with_sql() -> None:
        """Test cache configuration with SQL settings."""
        cache_config = CacheConfig(
            maxsize=CUSTOM_CACHE_MAXSIZE,
            folder_name="custom_cache",
            use_sql=True,
            preferred_engine="disk",
        )
    
>       assert cache_config.maxsize == CUSTOM_CACHE_MAXSIZE
E       AssertionError: assert None == 300
E        +  where None = CacheConfig(maxsize=300, folder_name='custom_cach
e', use_sql=True, preferred_engine='disk', cache_type=None).maxsize

tests/test_config.py:197: AssertionError
___________________ test_lru_cache_maxsize_enforcement ___________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x111bbcd40>

    def test_lru_cache_maxsize_enforcement(lru_engine: FunctoolsCacheEngin
e) -> None:
        """Test that LRU cache respects maxsize."""
        # Fill cache to maxsize
        for i in range(10):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == 10
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", 10), 10)
>       assert len(lru_engine._cache) == 10
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x111bbcd40>._cac
he

tests/test_engines.py:194: AssertionError
________________________ test_engine_registration ________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x111
ba3200>

    def test_engine_registration(engine_manager: EngineManager) -> None:
        """Test registration of cache engines."""
        # Default engines should be registered
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
>       assert isinstance(engine, CacheEngine)
E       assert False
E        +  where False = isinstance(<twat_cache.engines.functools.Functoo
lsCacheEngine object at 0x111bbce30>, CacheEngine)

tests/test_engines.py:260: AssertionError
_________________________ test_engine_selection __________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x111
ba3200>

    def test_engine_selection(engine_manager: EngineManager) -> None:
        """Test selection of appropriate cache engines."""
        # Test default selection (should be LRU)
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
        assert isinstance(engine, FunctoolsCacheEngine)
    
        # Test disk cache selection
>       config = CacheConfig(folder_name="test_cache")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:298: TypeError
_______________________ test_engine_configuration ________________________

    def test_engine_configuration() -> None:
        """Test engine configuration."""
        # Test maxsize configuration
>       config = CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:332: TypeError
________________________ test_unavailable_engine _________________________

    def test_unavailable_engine() -> None:
        """Test handling of unavailable engines."""
        # Test unavailable preferred engine
>       config = CacheConfig(preferred_engine="nonexistent")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:350: TypeError
__________________________ test_engine_caching ___________________________

test_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at
 0x111bbfec0>

    def test_engine_caching(test_engine: BaseCacheEngine[Any, Any]) -> Non
e:
        """Test basic caching functionality of an engine."""
        call_count = 0
    
        def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
    
        # First call should compute
        assert test_func(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
        assert test_engine.stats["hits"] == 0
    
        # Second call should use cache
        assert test_func(TEST_INPUT) == TEST_RESULT
>       assert call_count == 1
E       assert 2 == 1

tests/test_engines.py:398: AssertionError
____________________________ test_lru_maxsize ____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x111c585c0>

    def test_lru_maxsize(lru_engine: FunctoolsCacheEngine[Any, Any]) -> No
ne:
        """Test LRU cache maxsize enforcement."""
        # Fill cache to maxsize
        for i in range(LRU_CACHE_SIZE):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == LRU_CACHE_SIZE
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", LRU_CACHE_SIZE), LRU_CACHE_SI
ZE)
>       assert len(lru_engine._cache) == LRU_CACHE_SIZE
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x111c585c0>._cac
he

tests/test_engines.py:418: AssertionError
_____________________________ test_lru_stats _____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x111c58ec0>

    def test_lru_stats(lru_engine: FunctoolsCacheEngine[Any, Any]) -> None
:
        """Test LRU cache statistics."""
        # Add some items and access them
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some hits
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some misses
        lru_engine._get_cached_value("key3")
        lru_engine._get_cached_value("key4")
    
        # Check stats
        stats = lru_engine.stats
>       assert stats["hits"] == EXPECTED_CALL_COUNT
E       assert 0 == 2

tests/test_engines.py:452: AssertionError
======================== short test summary info =========================
FAILED tests/test_cache.py::test_cache_settings_validation - AttributeErro
r: 'dict' object has no attribute 'validate'
FAILED tests/test_cache.py::test_cache_clear - assert 1 == 2
FAILED tests/test_cache.py::test_cache_stats - assert 0 >= 2
FAILED tests/test_cache.py::test_cache_exceptions - assert 2 == 1
FAILED tests/test_cache.py::test_kwargs_handling - assert 2 == 1
FAILED tests/test_config.py::test_cache_config_validation - TypeError: Cac
heConfig.validate_maxsize() missing 1 required position...
FAILED tests/test_config.py::test_default_config - AssertionError: assert 
PosixPath('/Users/adam/Library/Caches/twat_cac...
FAILED tests/test_config.py::test_custom_config - AssertionError: assert 1
000 == 500
FAILED tests/test_config.py::test_get_cache_config - AssertionError: asser
t None == 1000
FAILED tests/test_config.py::test_cache_config_creation - AssertionError: 
assert None == 200
FAILED tests/test_config.py::test_cache_config_with_sql - AssertionError: 
assert None == 300
FAILED tests/test_engines.py::test_lru_cache_maxsize_enforcement - assert 
11 == 10
FAILED tests/test_engines.py::test_engine_registration - assert False
FAILED tests/test_engines.py::test_engine_selection - TypeError: CacheConf
ig() takes no arguments
FAILED tests/test_engines.py::test_engine_configuration - TypeError: Cache
Config() takes no arguments
FAILED tests/test_engines.py::test_unavailable_engine - TypeError: CacheCo
nfig() takes no arguments
FAILED tests/test_engines.py::test_engine_caching - assert 2 == 1
FAILED tests/test_engines.py::test_lru_maxsize - assert 11 == 10
FAILED tests/test_engines.py::test_lru_stats - assert 0 == 2
ERROR tests/test_engines.py::test_base_engine_initialization
ERROR tests/test_engines.py::test_base_engine_validation
ERROR tests/test_engines.py::test_lru_cache_initialization
ERROR tests/test_engines.py::test_engine_clear
ERROR tests/test_twat_cache.py::test_lru_cache_get_set - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_clear - TypeError: CacheCon
fig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_maxsize - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_disk_cache_persistence - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_joblib_numpy_array - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_klepto_persistence - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_async_cache_operations - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachebox_operations - TypeError: Cach
eConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachetools_operations - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_get_set - TypeError: 
CacheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_clear - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_maxsize - TypeError: 
CacheConfig() takes no arguments
================ 19 failed, 22 passed, 16 errors in 0.82s ================

```

---

_****_



I see several issues that need to be fixed. Let me address them one by one:

1. First, let's fix the CacheConfig initialization issue. The error `TypeError: CacheConfig() takes no arguments` suggests we need to update the model configuration.

---

_****_

```diff
  
  from pathlib import Path
- from typing import Literal
+ from typing import Literal, Any
  
  from loguru import logger
          "extra": "ignore",
          "arbitrary_types_allowed": True,
-     }
+         "from_attributes": True,
+     }
+ 
+     def model_post_init(self, __context: Any) -> None:
+         """Post-initialization validation."""
+         super().model_post_init(__context)
+         self.validate()
+ 
+     def validate(self) -> None:
+         """Validate all configuration settings."""
+         if self.maxsize is not None:
+             self.validate_maxsize(self.maxsize)
+         if self.folder_name is not None:
+             self.validate_folder_name(self.folder_name)
+         if self.cache_type is not None:
+             self.validate_cache_type(self.cache_type)
  
      @classmethod
```

---

_****_



Now let's fix the GlobalConfig class to properly handle environment variables and default values.

---

_****_

```diff
          "extra": "ignore",
          "arbitrary_types_allowed": True,
+         "from_attributes": True,
+         "use_enum_values": True,
      }
  
          default=1000,
          description="Default maximum cache size",
-         validation_alias="TWAT_CACHE_DEFAULT_MAXSIZE",
+         validation_alias="DEFAULT_MAXSIZE",
      )
      default_use_sql: bool = Field(
          default=False,
          description="Default SQL storage setting",
-         validation_alias="TWAT_CACHE_DEFAULT_USE_SQL",
+         validation_alias="DEFAULT_USE_SQL",
      )
      default_engine: str = Field(
          default="lru",
          description="Default cache engine",
-         validation_alias="TWAT_CACHE_DEFAULT_ENGINE",
+         validation_alias="DEFAULT_ENGINE",
      )
      default_cache_type: CacheType | None = Field(
          default=None,
          description="Default cache type (speed, database, filesystem)",
-         validation_alias="TWAT_CACHE_DEFAULT_TYPE",
+         validation_alias="DEFAULT_TYPE",
      )
  
          default=True,
          description="Enable data compression",
-         validation_alias="TWAT_CACHE_ENABLE_COMPRESSION",
+         validation_alias="ENABLE_COMPRESSION",
      )
      compression_level: int = Field(
          default=6,
          description="Compression level (1-9)",
-         validation_alias="TWAT_CACHE_COMPRESSION_LEVEL",
+         validation_alias="COMPRESSION_LEVEL",
      )
  
          default=False,
          description="Enable debug logging",
-         validation_alias="TWAT_CACHE_DEBUG",
+         validation_alias="DEBUG",
      )
      log_file: Path | None = Field(
          default=None,
          description="Log file path",
-         validation_alias="TWAT_CACHE_LOG_FILE",
+         validation_alias="LOG_FILE",
      )
  
          preferred_engine: str | None = None,
          cache_type: CacheType | None = None,
-     ) -> CacheConfigBase:
+     ) -> CacheConfig:
          """
          Get cache configuration with defaults.
  
          Returns:
-             Cache configuration object
+             CacheConfig: Cache configuration with defaults applied
          """
          return CacheConfig(
              maxsize=maxsize if maxsize is not None else self.default_maxsize,
              folder_name=folder_name,
              use_sql=use_sql if use_sql is not None else self.default_use_sql,
-             preferred_engine=(
-                 preferred_engine
+             preferred_engine=preferred_engine
              if preferred_engine is not None
-                 else self.default_engine
-             ),
-             cache_type=(
-                 cache_type if cache_type is not None else self.default_cache_type
-             ),
+             else self.default_engine,
+             cache_type=cache_type
+             if cache_type is not None
+             else self.default_cache_type,
          )
  
```

---

_****_





Now let's fix the FunctoolsCacheEngine to properly handle cache stats and maxsize enforcement.

---

_****_

Read file: src/twat_cache/engines/functools.py

---

_****_





Let me fix the FunctoolsCacheEngine implementation to properly handle cache stats and maxsize enforcement.

---

_****_

```diff
          """
          str_key = self._make_key(key) if not isinstance(key, str) else key
-         if len(self._cache) >= self._maxsize:
-             # Remove oldest item (LRU)
-             if self._cache_order:
+ 
+         # If key exists, update it
+         if str_key in self._cache:
+             self._cache[str_key] = value
+             if str_key in self._cache_order:
+                 self._cache_order.remove(str_key)
+                 self._cache_order.append(str_key)
+             return
+ 
+         # If cache is full, remove oldest item
+         while len(self._cache) >= self._maxsize and self._cache_order:
              oldest_key = self._cache_order.pop(0)
              self._cache.pop(oldest_key, None)
+ 
+         # Add new item
          self._cache[str_key] = value
-         if str_key in self._cache_order:
-             self._cache_order.remove(str_key)
          self._cache_order.append(str_key)
  
          self._cache.clear()
          self._cache_order.clear()
+         self._hits = 0
+         self._misses = 0
          logger.debug("Cleared functools cache")
  
      @property
      def stats(self) -> dict[str, Any]:
-         """Get cache statistics."""
+         """
+         Get cache statistics.
+ 
+         Returns:
+             dict: A dictionary containing cache statistics
+         """
          return {
              "type": "functools",
              "hits": self._hits,
              "misses": self._misses,
-             "size": len(self._cache),
+             "size": self._maxsize,
          }
  
  
      def cache(self, func: F) -> F:
-         """Apply functools caching to the function.
+         """
+         Decorate a function with caching behavior.
  
          Args:
-             func: Function to be cached
+             func: The function to cache
  
          Returns:
-             Cached function wrapper
+             A wrapped function with caching behavior
          """
  
              return result
  
-         # Store the wrapper function
-         wrapper.cache = self._cache  # type: ignore
-         wrapper.cache_order = self._cache_order  # type: ignore
+         # Preserve function metadata
+         wrapper.__name__ = func.__name__
+         wrapper.__doc__ = func.__doc__
+         wrapper.__module__ = func.__module__
          return cast(F, wrapper)
  
```

---

_****_





Now let's run the tests again to see if these changes have fixed the issues.

---

_****_

```bash
hatch run test
```

```
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pytest_asyncio/plugin.py:207:
PytestDeprecationWarning: The configuration option "asyncio_default_fixtur
e_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture
 caching scope. Future versions of pytest-asyncio will default the loop sc
ope for asynchronous fixtures to function scope. Set the default fixture l
oop scope explicitly in order to avoid unexpected behavior in the future.
Valid fixture loop scopes are: "function", "class", "module", "package", "
session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET
))
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1xkE/twat-c
ache/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_r
ounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=Fal
se warmup_iterations=100000)
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache
configfile: pyproject.toml
plugins: cov-6.0.0, asyncio-0.25.3, benchmark-5.1.0, xdist-3.6.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None
collected 57 items                                                       

tests/test_cache.py::test_cache_settings_validation FAILED         [  1%]
tests/test_cache.py::test_basic_caching PASSED                     [  3%]
tests/test_cache.py::test_cache_clear FAILED                       [  5%]
tests/test_cache.py::test_cache_stats FAILED                       [  7%]
tests/test_cache.py::test_list_processing PASSED                   [  8%]
tests/test_cache.py::test_different_backends PASSED                [ 10%]
tests/test_cache.py::test_cache_with_complex_types PASSED          [ 12%]
tests/test_cache.py::test_cache_exceptions FAILED                  [ 14%]
tests/test_cache.py::test_kwargs_handling FAILED                   [ 15%]
tests/test_config.py::test_cache_config_validation FAILED          [ 17%]
tests/test_config.py::test_default_config FAILED                   [ 19%]
tests/test_config.py::test_custom_config FAILED                    [ 21%]
tests/test_config.py::test_global_config_env_vars FAILED           [ 22%]
tests/test_config.py::test_get_cache_config FAILED                 [ 24%]
tests/test_config.py::test_logging_configuration PASSED            [ 26%]
tests/test_config.py::test_cache_config_creation FAILED            [ 28%]
tests/test_config.py::test_cache_config_with_sql FAILED            [ 29%]
tests/test_engines.py::test_base_engine_initialization ERROR       [ 31%]
tests/test_engines.py::test_base_engine_key_generation PASSED      [ 33%]
tests/test_engines.py::test_base_engine_cache_decorator PASSED     [ 35%]
tests/test_engines.py::test_base_engine_validation ERROR           [ 36%]
tests/test_engines.py::test_lru_cache_initialization ERROR         [ 38%]
tests/test_engines.py::test_lru_cache_maxsize_enforcement FAILED   [ 40%]
tests/test_engines.py::test_lru_cache_clear FAILED                 [ 42%]
tests/test_engines.py::test_lru_cache_with_complex_values PASSED   [ 43%]
tests/test_engines.py::test_lru_cache_stats_accuracy FAILED        [ 45%]
tests/test_engines.py::test_engine_registration FAILED             [ 47%]
tests/test_engines.py::test_engine_selection FAILED                [ 49%]
tests/test_engines.py::test_invalid_engine_registration PASSED     [ 50%]
tests/test_engines.py::test_engine_manager_singleton PASSED        [ 52%]
tests/test_engines.py::test_engine_configuration FAILED            [ 54%]
tests/test_engines.py::test_unavailable_engine FAILED              [ 56%]
tests/test_engines.py::test_engine_stats PASSED                    [ 57%]
tests/test_engines.py::test_engine_clear ERROR                     [ 59%]
tests/test_engines.py::test_engine_caching FAILED                  [ 61%]
tests/test_engines.py::test_lru_maxsize FAILED                     [ 63%]
tests/test_engines.py::test_lru_clear PASSED                       [ 64%]
tests/test_engines.py::test_lru_stats FAILED                       [ 66%]
tests/test_engines.py::test_functools_cache_maxsize_enforcement PASSED [ 6
8%]
tests/test_engines.py::test_functools_cache_clear PASSED           [ 70%]
tests/test_engines.py::test_functools_cache_with_complex_values PASSED [ 7
1%]
tests/test_engines.py::test_functools_cache_stats_accuracy PASSED  [ 73%]
tests/test_engines.py::test_functools_maxsize PASSED               [ 75%]
tests/test_engines.py::test_functools_clear PASSED                 [ 77%]
tests/test_engines.py::test_functools_stats PASSED                 [ 78%]
tests/test_twat_cache.py::test_lru_cache_get_set ERROR             [ 80%]
tests/test_twat_cache.py::test_lru_cache_clear ERROR               [ 82%]
tests/test_twat_cache.py::test_lru_cache_maxsize ERROR             [ 84%]
tests/test_twat_cache.py::test_disk_cache_persistence ERROR        [ 85%]
tests/test_twat_cache.py::test_joblib_numpy_array ERROR            [ 87%]
tests/test_twat_cache.py::test_klepto_persistence ERROR            [ 89%]
tests/test_twat_cache.py::test_async_cache_operations ERROR        [ 91%]
tests/test_twat_cache.py::test_cachebox_operations ERROR           [ 92%]
tests/test_twat_cache.py::test_cachetools_operations ERROR         [ 94%]
tests/test_twat_cache.py::test_functools_cache_get_set ERROR       [ 96%]
tests/test_twat_cache.py::test_functools_cache_clear ERROR         [ 98%]
tests/test_twat_cache.py::test_functools_cache_maxsize ERROR       [100%]

================================= ERRORS =================================
___________ ERROR at setup of test_base_engine_initialization ____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 110
  def test_base_engine_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:110
_____________ ERROR at setup of test_base_engine_validation ______________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 163
  def test_base_engine_validation(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:163
____________ ERROR at setup of test_lru_cache_initialization _____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 176
  def test_lru_cache_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:176
__________________ ERROR at setup of test_engine_clear ___________________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 365
  def test_engine_clear(engine: BaseCacheEngine[Any, Any]) -> None:
E       fixture 'engine' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:365
________________ ERROR at setup of test_lru_cache_get_set ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_________________ ERROR at setup of test_lru_cache_clear _________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
________________ ERROR at setup of test_lru_cache_maxsize ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_disk_cache_persistence ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_joblib_numpy_array ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_klepto_persistence ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_async_cache_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_cachebox_operations _______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_cachetools_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_get_set _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_functools_cache_clear ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_maxsize _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
================================ FAILURES ================================
_____________________ test_cache_settings_validation _____________________

    def test_cache_settings_validation() -> None:
        """Test validation of cache settings."""
        # Valid settings
        config = CacheConfig(maxsize=100)
>       config.validate()  # Should not raise
E       AttributeError: 'dict' object has no attribute 'validate'

tests/test_cache.py:32: AttributeError
____________________________ test_cache_clear ____________________________

    def test_cache_clear() -> None:
        """Test cache clearing functionality."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # First call
        assert cached_function(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
    
        # Clear cache
        clear_cache()
    
        # Should recompute after clear
        assert cached_function(TEST_INPUT) == TEST_RESULT
>       assert call_count == EXPECTED_CALL_COUNT
E       assert 1 == 2

tests/test_cache.py:96: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.626 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
5dd10943
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.627 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
9fc77f65
2025-02-16 07:00:07.628 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.628 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.628 | DEBUG    | twat_cache.cache:clear_cache:55 - Cle
aring cache for engine: FunctoolsCacheEngine
2025-02-16 07:00:07.628 | DEBUG    | twat_cache.engines.functools:clear:13
9 - Cleared functools cache
____________________________ test_cache_stats ____________________________

    def test_cache_stats() -> None:
        """Test cache statistics."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # Generate some cache activity
        for _i in range(3):
            cached_function(TEST_INPUT)
            cached_function(TEST_INPUT_2)
    
        # Get stats
        stats = get_stats()
    
        # Basic stats checks
        assert isinstance(stats, dict)
>       assert stats["hits"] >= MIN_STATS_COUNT
E       assert 0 >= 2

tests/test_cache.py:119: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.632 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
bc6c498f
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
48f63ae2
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.633 | DEBUG    | twat_cache.cache:get_stats:93 - Getti
ng stats for engine: FunctoolsCacheEngine
_________________________ test_cache_exceptions __________________________

    def test_cache_exceptions() -> None:
        """Test caching of exceptions."""
        call_count = 0
    
        @ucache(maxsize=100)
        def failing_function(x: int) -> None:
            nonlocal call_count
            call_count += 1
            msg = "Test error"
            raise ValueError(msg)
    
        # First call
        with pytest.raises(ValueError):
            failing_function(5)
        assert call_count == 1
    
        # Second call should not recompute
        with pytest.raises(ValueError):
            failing_function(5)
>       assert call_count == 1
E       assert 2 == 1

tests/test_cache.py:207: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.645 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.645 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
d2314edb
2025-02-16 07:00:07.645 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=100 folder_name=Non
e use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.645 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.645 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
__________________________ test_kwargs_handling __________________________

    def test_kwargs_handling() -> None:
        """Test caching with different keyword arguments."""
        call_count = 0
    
        @ucache()
        def kwarg_function(x: int, multiplier: int = 1) -> int:
            nonlocal call_count
            call_count += 1
            return x * multiplier
    
        # Test with different kwarg combinations
        assert kwarg_function(TEST_INPUT) == TEST_INPUT
        assert call_count == 1
    
        assert kwarg_function(TEST_INPUT, multiplier=1) == TEST_INPUT
>       assert call_count == 1  # Should use cache
E       assert 2 == 1

tests/test_cache.py:225: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.650 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:00:07.650 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
847ba3c8
2025-02-16 07:00:07.650 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:00:07.650 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:00:07.650 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
______________________ test_cache_config_validation ______________________

    def test_cache_config_validation() -> None:
        """Test validation of cache configuration."""
        # Valid configurations
        config = CacheConfig(maxsize=100)
>       config.validate_maxsize()  # Should not raise
E       TypeError: CacheConfig.validate_maxsize() missing 1 required posit
ional argument: 'v'

tests/test_config.py:52: TypeError
__________________________ test_default_config ___________________________

    def test_default_config() -> None:
        """Test default configuration values."""
        config = GlobalConfig()
    
        # Check default values
>       assert config.cache_dir == get_cache_path()
E       AssertionError: assert PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_78ddffb9') == PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_7b8cdd63')
E        +  where PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_78ddffb9') = GlobalConfig(cache_dir=PosixPath('/Users/adam/Library/Cac
hes/twat_cache/twat_cache_78ddffb9'), default_maxsize=1000, default_use_sq
l=False, default_engine='lru', default_cache_type=None, enable_compression
=True, compression_level=6, debug=False, log_file=None).cache_dir
E        +  and   PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_7b8cdd63') = get_cache_path()

tests/test_config.py:72: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.660 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
78ddffb9
2025-02-16 07:00:07.660 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
7b8cdd63
___________________________ test_custom_config ___________________________

    def test_custom_config() -> None:
        """Test custom configuration values."""
        config = GlobalConfig(
            default_maxsize=CUSTOM_MAXSIZE,
            default_use_sql=True,
            default_engine="disk",
            enable_compression=False,
            debug=True,
            log_file="cache.log",
        )
    
        # Check values
>       assert config.default_maxsize == CUSTOM_MAXSIZE
E       AssertionError: assert 1000 == 500
E        +  where 1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_69e138f2'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:94: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.667 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
69e138f2
______________________ test_global_config_env_vars _______________________

clean_env = None

    def test_global_config_env_vars(clean_env: None) -> None:
        """Test environment variable configuration."""
        # Set environment variables
        os.environ["TWAT_CACHE_DEFAULT_MAXSIZE"] = "500"
        os.environ["TWAT_CACHE_DEFAULT_USE_SQL"] = "true"
        os.environ["TWAT_CACHE_DEFAULT_ENGINE"] = "disk"
        os.environ["TWAT_CACHE_DEBUG"] = "true"
    
        # Create config with environment variables
        config = GlobalConfig()
    
        # Check values
>       assert config.default_maxsize == 500
E       AssertionError: assert 1000 == 500
E        +  where 1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_35ef79ef'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:114: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.672 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
35ef79ef
_________________________ test_get_cache_config __________________________

    def test_get_cache_config() -> None:
        """Test getting cache configuration with defaults."""
        global_config = GlobalConfig()
    
        # Test with no overrides
        cache_config = global_config.get_cache_config()
>       assert cache_config.maxsize == global_config.default_maxsize
E       AssertionError: assert None == 1000
E        +  where None = CacheConfig(maxsize=1000, folder_name=None, use_s
ql=False, preferred_engine='lru', cache_type=None).maxsize
E        +  and   1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_c1565773'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:126: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:00:07.679 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
c1565773
_______________________ test_cache_config_creation _______________________

    def test_cache_config_creation() -> None:
        """Test cache configuration creation."""
        global_config = GlobalConfig()
    
        # Create cache config with some overrides
        cache_config = CacheConfig(
            maxsize=CACHE_CONFIG_MAXSIZE,
            folder_name="test_cache",
        )
    
>       assert cache_config.maxsize == CACHE_CONFIG_MAXSIZE
E       AssertionError: assert None == 200
E        +  where None = CacheConfig(maxsize=200, folder_name='test_cache'
, use_sql=False, preferred_engine=None, cache_type=None).maxsize

tests/test_config.py:183: AssertionError
_______________________ test_cache_config_with_sql _______________________

    def test_cache_config_with_sql() -> None:
        """Test cache configuration with SQL settings."""
        cache_config = CacheConfig(
            maxsize=CUSTOM_CACHE_MAXSIZE,
            folder_name="custom_cache",
            use_sql=True,
            preferred_engine="disk",
        )
    
>       assert cache_config.maxsize == CUSTOM_CACHE_MAXSIZE
E       AssertionError: assert None == 300
E        +  where None = CacheConfig(maxsize=300, folder_name='custom_cach
e', use_sql=True, preferred_engine='disk', cache_type=None).maxsize

tests/test_config.py:197: AssertionError
___________________ test_lru_cache_maxsize_enforcement ___________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x1036f9610>

    def test_lru_cache_maxsize_enforcement(lru_engine: FunctoolsCacheEngin
e) -> None:
        """Test that LRU cache respects maxsize."""
        # Fill cache to maxsize
        for i in range(10):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == 10
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", 10), 10)
>       assert len(lru_engine._cache) == 10
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x1036f9610>._cac
he

tests/test_engines.py:194: AssertionError
__________________________ test_lru_cache_clear __________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x1036f9d30>

    def test_lru_cache_clear(lru_engine: FunctoolsCacheEngine) -> None:
        """Test cache clearing."""
        # Add some items
        for i in range(5):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == 5
    
        # Clear cache
        lru_engine.clear()
        assert len(lru_engine._cache) == 0
        assert lru_engine.stats["hits"] == 0
        assert lru_engine.stats["misses"] == 0
>       assert lru_engine.stats["size"] == 0
E       assert 100 == 0

tests/test_engines.py:212: AssertionError
_____________________ test_lru_cache_stats_accuracy ______________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x1036fa300>

    def test_lru_cache_stats_accuracy(lru_engine: FunctoolsCacheEngine) ->
 None:
        """Test that cache statistics are accurate."""
    
        @lru_engine.cache
        def test_func(x: int) -> int:
            return x * 2
    
        # Test hits and misses
        test_func(1)  # miss
        test_func(1)  # hit
        test_func(2)  # miss
        test_func(1)  # hit
    
        stats = lru_engine.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 2
>       assert stats["size"] == 2
E       assert 100 == 2

tests/test_engines.py:250: AssertionError
________________________ test_engine_registration ________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x102
acb260>

    def test_engine_registration(engine_manager: EngineManager) -> None:
        """Test registration of cache engines."""
        # Default engines should be registered
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
>       assert isinstance(engine, CacheEngine)
E       assert False
E        +  where False = isinstance(<twat_cache.engines.functools.Functoo
lsCacheEngine object at 0x1036faf90>, CacheEngine)

tests/test_engines.py:260: AssertionError
_________________________ test_engine_selection __________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x102
acb260>

    def test_engine_selection(engine_manager: EngineManager) -> None:
        """Test selection of appropriate cache engines."""
        # Test default selection (should be LRU)
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
        assert isinstance(engine, FunctoolsCacheEngine)
    
        # Test disk cache selection
>       config = CacheConfig(folder_name="test_cache")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:298: TypeError
_______________________ test_engine_configuration ________________________

    def test_engine_configuration() -> None:
        """Test engine configuration."""
        # Test maxsize configuration
>       config = CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:332: TypeError
________________________ test_unavailable_engine _________________________

    def test_unavailable_engine() -> None:
        """Test handling of unavailable engines."""
        # Test unavailable preferred engine
>       config = CacheConfig(preferred_engine="nonexistent")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:350: TypeError
__________________________ test_engine_caching ___________________________

test_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at
 0x1037a12e0>

    def test_engine_caching(test_engine: BaseCacheEngine[Any, Any]) -> Non
e:
        """Test basic caching functionality of an engine."""
        call_count = 0
    
        def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
    
        # First call should compute
        assert test_func(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
        assert test_engine.stats["hits"] == 0
    
        # Second call should use cache
        assert test_func(TEST_INPUT) == TEST_RESULT
>       assert call_count == 1
E       assert 2 == 1

tests/test_engines.py:398: AssertionError
____________________________ test_lru_maxsize ____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x1036fbf80>

    def test_lru_maxsize(lru_engine: FunctoolsCacheEngine[Any, Any]) -> No
ne:
        """Test LRU cache maxsize enforcement."""
        # Fill cache to maxsize
        for i in range(LRU_CACHE_SIZE):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == LRU_CACHE_SIZE
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", LRU_CACHE_SIZE), LRU_CACHE_SI
ZE)
>       assert len(lru_engine._cache) == LRU_CACHE_SIZE
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x1036fbf80>._cac
he

tests/test_engines.py:418: AssertionError
_____________________________ test_lru_stats _____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x1036fa3f0>

    def test_lru_stats(lru_engine: FunctoolsCacheEngine[Any, Any]) -> None
:
        """Test LRU cache statistics."""
        # Add some items and access them
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some hits
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some misses
        lru_engine._get_cached_value("key3")
        lru_engine._get_cached_value("key4")
    
        # Check stats
        stats = lru_engine.stats
>       assert stats["hits"] == EXPECTED_CALL_COUNT
E       assert 0 == 2

tests/test_engines.py:452: AssertionError
======================== short test summary info =========================
FAILED tests/test_cache.py::test_cache_settings_validation - AttributeErro
r: 'dict' object has no attribute 'validate'
FAILED tests/test_cache.py::test_cache_clear - assert 1 == 2
FAILED tests/test_cache.py::test_cache_stats - assert 0 >= 2
FAILED tests/test_cache.py::test_cache_exceptions - assert 2 == 1
FAILED tests/test_cache.py::test_kwargs_handling - assert 2 == 1
FAILED tests/test_config.py::test_cache_config_validation - TypeError: Cac
heConfig.validate_maxsize() missing 1 required position...
FAILED tests/test_config.py::test_default_config - AssertionError: assert 
PosixPath('/Users/adam/Library/Caches/twat_cac...
FAILED tests/test_config.py::test_custom_config - AssertionError: assert 1
000 == 500
FAILED tests/test_config.py::test_global_config_env_vars - AssertionError:
 assert 1000 == 500
FAILED tests/test_config.py::test_get_cache_config - AssertionError: asser
t None == 1000
FAILED tests/test_config.py::test_cache_config_creation - AssertionError: 
assert None == 200
FAILED tests/test_config.py::test_cache_config_with_sql - AssertionError: 
assert None == 300
FAILED tests/test_engines.py::test_lru_cache_maxsize_enforcement - assert 
11 == 10
FAILED tests/test_engines.py::test_lru_cache_clear - assert 100 == 0
FAILED tests/test_engines.py::test_lru_cache_stats_accuracy - assert 100 =
= 2
FAILED tests/test_engines.py::test_engine_registration - assert False
FAILED tests/test_engines.py::test_engine_selection - TypeError: CacheConf
ig() takes no arguments
FAILED tests/test_engines.py::test_engine_configuration - TypeError: Cache
Config() takes no arguments
FAILED tests/test_engines.py::test_unavailable_engine - TypeError: CacheCo
nfig() takes no arguments
FAILED tests/test_engines.py::test_engine_caching - assert 2 == 1
FAILED tests/test_engines.py::test_lru_maxsize - assert 11 == 10
FAILED tests/test_engines.py::test_lru_stats - assert 0 == 2
ERROR tests/test_engines.py::test_base_engine_initialization
ERROR tests/test_engines.py::test_base_engine_validation
ERROR tests/test_engines.py::test_lru_cache_initialization
ERROR tests/test_engines.py::test_engine_clear
ERROR tests/test_twat_cache.py::test_lru_cache_get_set - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_clear - TypeError: CacheCon
fig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_maxsize - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_disk_cache_persistence - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_joblib_numpy_array - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_klepto_persistence - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_async_cache_operations - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachebox_operations - TypeError: Cach
eConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachetools_operations - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_get_set - TypeError: 
CacheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_clear - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_maxsize - TypeError: 
CacheConfig() takes no arguments
================ 22 failed, 19 passed, 16 errors in 0.69s ================

```

---

_****_





I see several issues that need to be fixed:

1. CacheConfig initialization is still not working properly
2. Environment variables are not being picked up in GlobalConfig
3. Cache stats and maxsize enforcement in FunctoolsCacheEngine need fixing

Let's fix these issues one by one. First, let's fix the CacheConfig initialization.

---

_****_

Read file: src/twat_cache/types.py

---

_****_





I see the issue. The CacheConfig in types.py is an abstract base class, but we're trying to use it directly in config.py. Let's fix this by updating the CacheConfig class in config.py to properly implement the abstract base class.

---

_****_

```diff
  
  
- class CacheConfig(BaseModel, CacheConfigBase):
+ class CacheConfig(BaseModel):
      """
      Cache configuration model.
      """
  
-     maxsize: int | None = Field(
+     _maxsize: int | None = Field(
          default=None,
+         alias="maxsize",
          description="Maximum number of items to store in the cache",
      )
-     folder_name: str | None = Field(
+     _folder_name: str | None = Field(
          default=None,
+         alias="folder_name",
          description="Name of the folder to store cache files in",
      )
-     use_sql: bool = Field(
+     _use_sql: bool = Field(
          default=False,
+         alias="use_sql",
          description="Whether to use SQL-based storage",
      )
-     preferred_engine: str | None = Field(
+     _preferred_engine: str | None = Field(
          default=None,
+         alias="preferred_engine",
          description="Preferred cache engine to use",
      )
-     cache_type: CacheType | None = Field(
+     _cache_type: CacheType | None = Field(
          default=None,
+         alias="cache_type",
          description="Type of cache to use (speed, database, filesystem)",
      )
          "arbitrary_types_allowed": True,
          "from_attributes": True,
-     }
- 
-     def model_post_init(self, __context: Any) -> None:
-         """Post-initialization validation."""
-         super().model_post_init(__context)
-         self.validate()
+         "populate_by_name": True,
+     }
+ 
+     @property
+     def maxsize(self) -> int | None:
+         """Maximum number of items to store in the cache."""
+         return self._maxsize
+ 
+     @property
+     def folder_name(self) -> str | None:
+         """Name of the folder to store cache files in."""
+         return self._folder_name
+ 
+     @property
+     def use_sql(self) -> bool:
+         """Whether to use SQL-based storage."""
+         return self._use_sql
+ 
+     @property
+     def preferred_engine(self) -> str | None:
+         """Preferred cache engine to use."""
+         return self._preferred_engine
+ 
+     @property
+     def cache_type(self) -> CacheType | None:
+         """Type of cache to use."""
+         return self._cache_type
  
      def validate(self) -> None:
          """Validate all configuration settings."""
-         if self.maxsize is not None:
-             self.validate_maxsize(self.maxsize)
-         if self.folder_name is not None:
-             self.validate_folder_name(self.folder_name)
-         if self.cache_type is not None:
-             self.validate_cache_type(self.cache_type)
+         if self._maxsize is not None:
+             self.validate_maxsize(self._maxsize)
+         if self._folder_name is not None:
+             self.validate_folder_name(self._folder_name)
+         if self._cache_type is not None:
+             self.validate_cache_type(self._cache_type)
  
      @classmethod
-     @field_validator("maxsize")
+     @field_validator("_maxsize")
      def validate_maxsize(cls, v: int | None) -> int | None:
          """Validate maxsize setting."""
  
      @classmethod
-     @field_validator("folder_name")
+     @field_validator("_folder_name")
      def validate_folder_name(cls, v: str | None) -> str | None:
          """Validate folder name setting."""
  
      @classmethod
-     @field_validator("cache_type")
+     @field_validator("_cache_type")
      def validate_cache_type(cls, v: CacheType | None) -> CacheType | None:
          """Validate cache type setting."""
```

---

_****_







Now let's fix the GlobalConfig class to properly handle environment variables.

---

_****_

```diff
          "from_attributes": True,
          "use_enum_values": True,
+         "populate_by_name": True,
      }
  
          default_factory=get_cache_path,
          description="Base directory for cache storage",
+         env="CACHE_DIR",
      )
  
          default=1000,
          description="Default maximum cache size",
-         validation_alias="DEFAULT_MAXSIZE",
+         env="DEFAULT_MAXSIZE",
      )
      default_use_sql: bool = Field(
          default=False,
          description="Default SQL storage setting",
-         validation_alias="DEFAULT_USE_SQL",
+         env="DEFAULT_USE_SQL",
      )
      default_engine: str = Field(
          default="lru",
          description="Default cache engine",
-         validation_alias="DEFAULT_ENGINE",
+         env="DEFAULT_ENGINE",
      )
      default_cache_type: CacheType | None = Field(
          default=None,
          description="Default cache type (speed, database, filesystem)",
-         validation_alias="DEFAULT_TYPE",
+         env="DEFAULT_TYPE",
      )
  
          default=True,
          description="Enable data compression",
-         validation_alias="ENABLE_COMPRESSION",
+         env="ENABLE_COMPRESSION",
      )
      compression_level: int = Field(
          default=6,
          description="Compression level (1-9)",
-         validation_alias="COMPRESSION_LEVEL",
+         env="COMPRESSION_LEVEL",
      )
  
          default=False,
          description="Enable debug logging",
-         validation_alias="DEBUG",
+         env="DEBUG",
      )
      log_file: Path | None = Field(
          default=None,
          description="Log file path",
-         validation_alias="LOG_FILE",
+         env="LOG_FILE",
      )
- 
-     @classmethod
-     @field_validator("compression_level")
-     def validate_compression_level(cls, v: int) -> int:
-         """Validate compression level."""
-         if not 1 <= v <= 9:
-             msg = "compression_level must be between 1 and 9"
-             raise ValueError(msg)
-         return v
- 
-     @classmethod
-     @field_validator("log_file")
-     def validate_log_file(cls, v: Path | None | str) -> Path | None:
-         """Validate log file path."""
-         if v is None:
-             return None
-         if isinstance(v, str):
-             v = Path(v)
-         if not v.parent.exists():
-             v.parent.mkdir(parents=True, exist_ok=True)
-         return v
  
      def get_cache_config(
              CacheConfig: Cache configuration with defaults applied
          """
-         return CacheConfig(
+         config = CacheConfig(
              maxsize=maxsize if maxsize is not None else self.default_maxsize,
              folder_name=folder_name,
              else self.default_cache_type,
          )
+         config.validate()
+         return config
+ 
+     @classmethod
+     @field_validator("compression_level")
+     def validate_compression_level(cls, v: int) -> int:
+         """Validate compression level."""
+         if not 1 <= v <= 9:
+             msg = "compression_level must be between 1 and 9"
+             raise ValueError(msg)
+         return v
+ 
+     @classmethod
+     @field_validator("log_file")
+     def validate_log_file(cls, v: Path | None | str) -> Path | None:
+         """Validate log file path."""
+         if v is None:
+             return None
+         if isinstance(v, str):
+             v = Path(v)
+         if not v.parent.exists():
+             v.parent.mkdir(parents=True, exist_ok=True)
+         return v
  
      def configure_logging(self) -> None:
```

---

_****_







Now let's fix the FunctoolsCacheEngine to properly handle cache stats and maxsize enforcement.

---

_****_

```diff
              return
  
-         # If cache is full, remove oldest item
+         # If cache is full, remove oldest items until we have space
          while len(self._cache) >= self._maxsize and self._cache_order:
              oldest_key = self._cache_order.pop(0)
              "hits": self._hits,
              "misses": self._misses,
-             "size": self._maxsize,
+             "size": len(self._cache),
          }
  
              result = self._get_cached_value(key)
              if result is None:
+                 try:
                      result = func(*args, **kwargs)
                      self._set_cached_value(key, result)
+                 except Exception as e:
+                     # Cache the exception to avoid recomputing
+                     self._set_cached_value(key, e)
+                     raise
+             elif isinstance(result, Exception):
+                 raise result
              return result
  
```

---

_****_







Now let's run the tests again to see if these changes have fixed the issues.

---

_****_

```bash
hatch run test
```

```
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pytest_asyncio/plugin.py:207:
PytestDeprecationWarning: The configuration option "asyncio_default_fixtur
e_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture
 caching scope. Future versions of pytest-asyncio will default the loop sc
ope for asynchronous fixtures to function scope. Set the default fixture l
oop scope explicitly in order to avoid unexpected behavior in the future.
Valid fixture loop scopes are: "function", "class", "module", "package", "
session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET
))
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1xkE/twat-c
ache/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_r
ounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=Fal
se warmup_iterations=100000)
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache
configfile: pyproject.toml
plugins: cov-6.0.0, asyncio-0.25.3, benchmark-5.1.0, xdist-3.6.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None
collected 0 items / 4 errors                                             

================================= ERRORS =================================
__________________ ERROR collecting tests/test_cache.py __________________
tests/test_cache.py:15: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel):
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:113: in __new__
    private_attributes = inspect_namespace(
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:425: in inspect_namespace
    raise NameError(
E   NameError: Fields must not use names with leading underscores; e.g., u
se 'maxsize' instead of '_maxsize'.
_________________ ERROR collecting tests/test_config.py __________________
tests/test_config.py:19: in <module>
    from twat_cache.config import CacheConfig, GlobalConfig
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel):
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:113: in __new__
    private_attributes = inspect_namespace(
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:425: in inspect_namespace
    raise NameError(
E   NameError: Fields must not use names with leading underscores; e.g., u
se 'maxsize' instead of '_maxsize'.
_________________ ERROR collecting tests/test_engines.py _________________
tests/test_engines.py:24: in <module>
    from twat_cache.engines.base import BaseCacheEngine
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel):
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:113: in __new__
    private_attributes = inspect_namespace(
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:425: in inspect_namespace
    raise NameError(
E   NameError: Fields must not use names with leading underscores; e.g., u
se 'maxsize' instead of '_maxsize'.
_______________ ERROR collecting tests/test_twat_cache.py ________________
tests/test_twat_cache.py:20: in <module>
    from twat_cache.engines.functools import FunctoolsCacheEngine
src/twat_cache/__init__.py:5: in <module>
    from twat_cache.cache import clear_cache, get_stats
src/twat_cache/cache.py:20: in <module>
    from .config import CacheConfig
src/twat_cache/config.py:32: in <module>
    class CacheConfig(BaseModel):
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:113: in __new__
    private_attributes = inspect_namespace(
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pydantic/_internal/_model_cons
truction.py:425: in inspect_namespace
    raise NameError(
E   NameError: Fields must not use names with leading underscores; e.g., u
se 'maxsize' instead of '_maxsize'.
======================== short test summary info =========================
ERROR tests/test_cache.py - NameError: Fields must not use names with lead
ing underscores; e.g., ...
ERROR tests/test_config.py - NameError: Fields must not use names with lea
ding underscores; e.g., ...
ERROR tests/test_engines.py - NameError: Fields must not use names with le
ading underscores; e.g., ...
ERROR tests/test_twat_cache.py - NameError: Fields must not use names with
 leading underscores; e.g., ...
!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!
=========================== 4 errors in 0.39s ============================

```

---

_****_





I see the issue. Pydantic doesn't allow field names with leading underscores. Let's fix the CacheConfig class to use proper field names.

---

_****_



---

_****_



I apologize for the confusion. Let me try again with the correct changes.

---

_****_

```diff
  
  
- class CacheConfig(BaseModel):
+ class CacheConfig(BaseModel, CacheConfigBase):
      """
      Cache configuration model.
      """
  
-     _maxsize: int | None = Field(
+     maxsize: int | None = Field(
          default=None,
-         alias="maxsize",
          description="Maximum number of items to store in the cache",
      )
-     _folder_name: str | None = Field(
+     folder_name: str | None = Field(
          default=None,
-         alias="folder_name",
          description="Name of the folder to store cache files in",
      )
-     _use_sql: bool = Field(
+     use_sql: bool = Field(
          default=False,
-         alias="use_sql",
          description="Whether to use SQL-based storage",
      )
-     _preferred_engine: str | None = Field(
+     preferred_engine: str | None = Field(
          default=None,
-         alias="preferred_engine",
          description="Preferred cache engine to use",
      )
-     _cache_type: CacheType | None = Field(
+     cache_type: CacheType | None = Field(
          default=None,
-         alias="cache_type",
          description="Type of cache to use (speed, database, filesystem)",
      )
      }
  
-     @property
-     def maxsize(self) -> int | None:
-         """Maximum number of items to store in the cache."""
-         return self._maxsize
- 
-     @property
-     def folder_name(self) -> str | None:
-         """Name of the folder to store cache files in."""
-         return self._folder_name
- 
-     @property
-     def use_sql(self) -> bool:
-         """Whether to use SQL-based storage."""
-         return self._use_sql
- 
-     @property
-     def preferred_engine(self) -> str | None:
-         """Preferred cache engine to use."""
-         return self._preferred_engine
- 
-     @property
-     def cache_type(self) -> CacheType | None:
-         """Type of cache to use."""
-         return self._cache_type
- 
      def validate(self) -> None:
          """Validate all configuration settings."""
-         if self._maxsize is not None:
-             self.validate_maxsize(self._maxsize)
-         if self._folder_name is not None:
-             self.validate_folder_name(self._folder_name)
-         if self._cache_type is not None:
-             self.validate_cache_type(self._cache_type)
+         if self.maxsize is not None:
+             self.validate_maxsize(self.maxsize)
+         if self.folder_name is not None:
+             self.validate_folder_name(self.folder_name)
+         if self.cache_type is not None:
+             self.validate_cache_type(self.cache_type)
  
      @classmethod
-     @field_validator("_maxsize")
+     @field_validator("maxsize")
      def validate_maxsize(cls, v: int | None) -> int | None:
          """Validate maxsize setting."""
  
      @classmethod
-     @field_validator("_folder_name")
+     @field_validator("folder_name")
      def validate_folder_name(cls, v: str | None) -> str | None:
          """Validate folder name setting."""
  
      @classmethod
-     @field_validator("_cache_type")
+     @field_validator("cache_type")
      def validate_cache_type(cls, v: CacheType | None) -> CacheType | None:
          """Validate cache type setting."""
          return v
  
+     def model_post_init(self, __context: Any) -> None:
+         """Post-initialization validation."""
+         super().model_post_init(__context)
+         self.validate()
+ 
  
  class GlobalConfig(BaseSettings):
```

---

_****_







Now let's run the tests again to see if these changes have fixed the issues.

---

_****_

```bash
hatch run test
```

```
/Users/adam/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1
xkE/twat-cache/lib/python3.12/site-packages/pytest_asyncio/plugin.py:207:
PytestDeprecationWarning: The configuration option "asyncio_default_fixtur
e_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture
 caching scope. Future versions of pytest-asyncio will default the loop sc
ope for asynchronous fixtures to function scope. Set the default fixture l
oop scope explicitly in order to avoid unexpected behavior in the future.
Valid fixture loop scopes are: "function", "class", "module", "package", "
session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET
))
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Library/Application Support/hatch/env/virtual/twat-cache/ivvP1xkE/twat-c
ache/bin/python
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_r
ounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=Fal
se warmup_iterations=100000)
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache
configfile: pyproject.toml
plugins: cov-6.0.0, asyncio-0.25.3, benchmark-5.1.0, xdist-3.6.1
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None
collected 57 items                                                       

tests/test_cache.py::test_cache_settings_validation FAILED         [  1%]
tests/test_cache.py::test_basic_caching PASSED                     [  3%]
tests/test_cache.py::test_cache_clear FAILED                       [  5%]
tests/test_cache.py::test_cache_stats FAILED                       [  7%]
tests/test_cache.py::test_list_processing PASSED                   [  8%]
tests/test_cache.py::test_different_backends PASSED                [ 10%]
tests/test_cache.py::test_cache_with_complex_types PASSED          [ 12%]
tests/test_cache.py::test_cache_exceptions PASSED                  [ 14%]
tests/test_cache.py::test_kwargs_handling FAILED                   [ 15%]
tests/test_config.py::test_cache_config_validation FAILED          [ 17%]
tests/test_config.py::test_default_config FAILED                   [ 19%]
tests/test_config.py::test_custom_config FAILED                    [ 21%]
tests/test_config.py::test_global_config_env_vars PASSED           [ 22%]
tests/test_config.py::test_get_cache_config FAILED                 [ 24%]
tests/test_config.py::test_logging_configuration FAILED            [ 26%]
tests/test_config.py::test_cache_config_creation FAILED            [ 28%]
tests/test_config.py::test_cache_config_with_sql FAILED            [ 29%]
tests/test_engines.py::test_base_engine_initialization ERROR       [ 31%]
tests/test_engines.py::test_base_engine_key_generation PASSED      [ 33%]
tests/test_engines.py::test_base_engine_cache_decorator PASSED     [ 35%]
tests/test_engines.py::test_base_engine_validation ERROR           [ 36%]
tests/test_engines.py::test_lru_cache_initialization ERROR         [ 38%]
tests/test_engines.py::test_lru_cache_maxsize_enforcement FAILED   [ 40%]
tests/test_engines.py::test_lru_cache_clear PASSED                 [ 42%]
tests/test_engines.py::test_lru_cache_with_complex_values PASSED   [ 43%]
tests/test_engines.py::test_lru_cache_stats_accuracy PASSED        [ 45%]
tests/test_engines.py::test_engine_registration FAILED             [ 47%]
tests/test_engines.py::test_engine_selection FAILED                [ 49%]
tests/test_engines.py::test_invalid_engine_registration PASSED     [ 50%]
tests/test_engines.py::test_engine_manager_singleton PASSED        [ 52%]
tests/test_engines.py::test_engine_configuration FAILED            [ 54%]
tests/test_engines.py::test_unavailable_engine FAILED              [ 56%]
tests/test_engines.py::test_engine_stats PASSED                    [ 57%]
tests/test_engines.py::test_engine_clear ERROR                     [ 59%]
tests/test_engines.py::test_engine_caching FAILED                  [ 61%]
tests/test_engines.py::test_lru_maxsize FAILED                     [ 63%]
tests/test_engines.py::test_lru_clear PASSED                       [ 64%]
tests/test_engines.py::test_lru_stats FAILED                       [ 66%]
tests/test_engines.py::test_functools_cache_maxsize_enforcement PASSED [ 6
8%]
tests/test_engines.py::test_functools_cache_clear PASSED           [ 70%]
tests/test_engines.py::test_functools_cache_with_complex_values PASSED [ 7
1%]
tests/test_engines.py::test_functools_cache_stats_accuracy PASSED  [ 73%]
tests/test_engines.py::test_functools_maxsize PASSED               [ 75%]
tests/test_engines.py::test_functools_clear PASSED                 [ 77%]
tests/test_engines.py::test_functools_stats PASSED                 [ 78%]
tests/test_twat_cache.py::test_lru_cache_get_set ERROR             [ 80%]
tests/test_twat_cache.py::test_lru_cache_clear ERROR               [ 82%]
tests/test_twat_cache.py::test_lru_cache_maxsize ERROR             [ 84%]
tests/test_twat_cache.py::test_disk_cache_persistence ERROR        [ 85%]
tests/test_twat_cache.py::test_joblib_numpy_array ERROR            [ 87%]
tests/test_twat_cache.py::test_klepto_persistence ERROR            [ 89%]
tests/test_twat_cache.py::test_async_cache_operations ERROR        [ 91%]
tests/test_twat_cache.py::test_cachebox_operations ERROR           [ 92%]
tests/test_twat_cache.py::test_cachetools_operations ERROR         [ 94%]
tests/test_twat_cache.py::test_functools_cache_get_set ERROR       [ 96%]
tests/test_twat_cache.py::test_functools_cache_clear ERROR         [ 98%]
tests/test_twat_cache.py::test_functools_cache_maxsize ERROR       [100%]

================================= ERRORS =================================
___________ ERROR at setup of test_base_engine_initialization ____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 110
  def test_base_engine_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:110
_____________ ERROR at setup of test_base_engine_validation ______________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 163
  def test_base_engine_validation(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:163
____________ ERROR at setup of test_lru_cache_initialization _____________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 176
  def test_lru_cache_initialization(test_config: TestConfig) -> None:
E       fixture 'test_config' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:176
__________________ ERROR at setup of test_engine_clear ___________________
file /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twa
t/plugins/repos/twat_cache/tests/test_engines.py, line 365
  def test_engine_clear(engine: BaseCacheEngine[Any, Any]) -> None:
E       fixture 'engine' not found
>       available fixtures: _session_event_loop, base_config, benchmark, b
enchmark_weave, cache, capfd, capfdbinary, caplog, capsys, capsysbinary, c
ov, doctest_namespace, engine_manager, event_loop, event_loop_policy, func
tools_engine, lru_engine, monkeypatch, no_cover, pytestconfig, record_prop
erty, record_testsuite_property, record_xml_attribute, recwarn, test_engin
e, testrun_uid, tests/test_engines.py::<event_loop>, tmp_path, tmp_path_fa
ctory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, u
nused_udp_port, unused_udp_port_factory, worker_id
>       use 'pytest --fixtures [testpath]' for help on them.

/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/tests/test_engines.py:365
________________ ERROR at setup of test_lru_cache_get_set ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_________________ ERROR at setup of test_lru_cache_clear _________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
________________ ERROR at setup of test_lru_cache_maxsize ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_disk_cache_persistence ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_joblib_numpy_array ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_klepto_persistence ________________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_async_cache_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_______________ ERROR at setup of test_cachebox_operations _______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_cachetools_operations ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_get_set _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
______________ ERROR at setup of test_functools_cache_clear ______________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
_____________ ERROR at setup of test_functools_cache_maxsize _____________

    @pytest.fixture
    def base_config() -> CacheConfig:
        """Provide a basic cache configuration."""
>       return CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_twat_cache.py:41: TypeError
================================ FAILURES ================================
_____________________ test_cache_settings_validation _____________________

    def test_cache_settings_validation() -> None:
        """Test validation of cache settings."""
        # Valid settings
        config = CacheConfig(maxsize=100)
>       config.validate()  # Should not raise
E       AttributeError: 'dict' object has no attribute 'validate'

tests/test_cache.py:32: AttributeError
____________________________ test_cache_clear ____________________________

    def test_cache_clear() -> None:
        """Test cache clearing functionality."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # First call
        assert cached_function(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
    
        # Clear cache
        clear_cache()
    
        # Should recompute after clear
        assert cached_function(TEST_INPUT) == TEST_RESULT
>       assert call_count == EXPECTED_CALL_COUNT
E       assert 1 == 2

tests/test_cache.py:96: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.364 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
9f587e3b
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
e0f83aac
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.cache:clear_cache:55 - Cle
aring cache for engine: FunctoolsCacheEngine
2025-02-16 07:02:08.365 | DEBUG    | twat_cache.engines.functools:clear:13
9 - Cleared functools cache
____________________________ test_cache_stats ____________________________

    def test_cache_stats() -> None:
        """Test cache statistics."""
        call_count = 0
    
        @ucache()
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * x
    
        # Generate some cache activity
        for _i in range(3):
            cached_function(TEST_INPUT)
            cached_function(TEST_INPUT_2)
    
        # Get stats
        stats = get_stats()
    
        # Basic stats checks
        assert isinstance(stats, dict)
>       assert stats["hits"] >= MIN_STATS_COUNT
E       assert 0 >= 2

tests/test_cache.py:119: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.371 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:02:08.371 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
db6307ab
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
9d843073
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:02:08.372 | DEBUG    | twat_cache.cache:get_stats:93 - Getti
ng stats for engine: FunctoolsCacheEngine
__________________________ test_kwargs_handling __________________________

    def test_kwargs_handling() -> None:
        """Test caching with different keyword arguments."""
        call_count = 0
    
        @ucache()
        def kwarg_function(x: int, multiplier: int = 1) -> int:
            nonlocal call_count
            call_count += 1
            return x * multiplier
    
        # Test with different kwarg combinations
        assert kwarg_function(TEST_INPUT) == TEST_INPUT
        assert call_count == 1
    
        assert kwarg_function(TEST_INPUT, multiplier=1) == TEST_INPUT
>       assert call_count == 1  # Should use cache
E       assert 2 == 1

tests/test_cache.py:225: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.388 | DEBUG    | twat_cache.engines.manager:_create_fa
llback_engine:227 - Using LRU cache
2025-02-16 07:02:08.388 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
04d78910
2025-02-16 07:02:08.388 | DEBUG    | twat_cache.engines.base:__init__:55 -
 Initialized FunctoolsCacheEngine with config: maxsize=None folder_name=No
ne use_sql=False preferred_engine=None cache_type=None
2025-02-16 07:02:08.388 | DEBUG    | twat_cache.engines.functools:__init__
:48 - Initialized functools cache with maxsize: 128
2025-02-16 07:02:08.388 | DEBUG    | twat_cache.decorators:decorator:68 - 
Using cache engine: FunctoolsCacheEngine
______________________ test_cache_config_validation ______________________

    def test_cache_config_validation() -> None:
        """Test validation of cache configuration."""
        # Valid configurations
        config = CacheConfig(maxsize=100)
>       config.validate_maxsize()  # Should not raise
E       TypeError: CacheConfig.validate_maxsize() missing 1 required posit
ional argument: 'v'

tests/test_config.py:52: TypeError
__________________________ test_default_config ___________________________

    def test_default_config() -> None:
        """Test default configuration values."""
        config = GlobalConfig()
    
        # Check default values
>       assert config.cache_dir == get_cache_path()
E       AssertionError: assert PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_8f0e6dd9') == PosixPath('/Users/adam/Library/Caches/twat_
cache/twat_cache_f9193c59')
E        +  where PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_8f0e6dd9') = GlobalConfig(cache_dir=PosixPath('/Users/adam/Library/Cac
hes/twat_cache/twat_cache_8f0e6dd9'), default_maxsize=1000, default_use_sq
l=False, default_engine='lru', default_cache_type=None, enable_compression
=True, compression_level=6, debug=False, log_file=None).cache_dir
E        +  and   PosixPath('/Users/adam/Library/Caches/twat_cache/twat_ca
che_f9193c59') = get_cache_path()

tests/test_config.py:72: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.401 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
8f0e6dd9
2025-02-16 07:02:08.402 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
f9193c59
___________________________ test_custom_config ___________________________

    def test_custom_config() -> None:
        """Test custom configuration values."""
        config = GlobalConfig(
            default_maxsize=CUSTOM_MAXSIZE,
            default_use_sql=True,
            default_engine="disk",
            enable_compression=False,
            debug=True,
            log_file="cache.log",
        )
    
        # Check values
        assert config.default_maxsize == CUSTOM_MAXSIZE
        assert config.default_use_sql is True
        assert config.default_engine == "disk"
        assert config.enable_compression is False
        assert config.debug is True
>       assert config.log_file == "cache.log"
E       AssertionError: assert PosixPath('cache.log') == 'cache.log'
E        +  where PosixPath('cache.log') = GlobalConfig(cache_dir=PosixPat
h('/Users/adam/Library/Caches/twat_cache/twat_cache_fea7caed'), default_ma
xsize=500, default_use_sql=True, default_engine='disk', default_cache_type
=None, enable_compression=False, compression_level=6, debug=True, log_file
=PosixPath('cache.log')).log_file

tests/test_config.py:99: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.408 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
fea7caed
_________________________ test_get_cache_config __________________________

    def test_get_cache_config() -> None:
        """Test getting cache configuration with defaults."""
        global_config = GlobalConfig()
    
        # Test with no overrides
        cache_config = global_config.get_cache_config()
>       assert cache_config.maxsize == global_config.default_maxsize
E       AssertionError: assert None == 1000
E        +  where None = CacheConfig(maxsize=1000, folder_name=None, use_s
ql=False, preferred_engine='lru', cache_type=None).maxsize
E        +  and   1000 = GlobalConfig(cache_dir=PosixPath('/Users/adam/Lib
rary/Caches/twat_cache/twat_cache_bf5abdf6'), default_maxsize=1000, defaul
t_use_sql=False, default_engine='lru', default_cache_type=None, enable_com
pression=True, compression_level=6, debug=False, log_file=None).default_ma
xsize

tests/test_config.py:126: AssertionError
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.419 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
bf5abdf6
_______________________ test_logging_configuration _______________________

tmp_path = PosixPath('/private/var/folders/05/clcynl0509ldxltl599hhhx40000
gn/T/pytest-of-adam/pytest-16/test_logging_configuration0')

    def test_logging_configuration(tmp_path: Path) -> None:
        """Test logging configuration."""
        # Test debug logging
        config = GlobalConfig(debug=True)
        config.configure_logging()
        # Debug logging should be enabled (no easy way to test this direct
ly)
    
        # Test file logging
        log_file = tmp_path / "cache.log"
        config = GlobalConfig(log_file=log_file)
        config.configure_logging()
        # Log file should be created when logging occurs
    
>       assert not log_file.exists()  # File not created until first log
E       AssertionError: assert not True
E        +  where True = exists()
E        +    where exists = PosixPath('/private/var/folders/05/clcynl0509
ldxltl599hhhx40000gn/T/pytest-of-adam/pytest-16/test_logging_configuration
0/cache.log').exists

tests/test_config.py:166: AssertionError
-------------------------- Captured stdout call --------------------------
2025-02-16 07:02:08 | DEBUG    | twat_cache.paths:get_cache_path:70 - Crea
ted cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_fee5
ebd8
-------------------------- Captured stderr call --------------------------
2025-02-16 07:02:08.429 | DEBUG    | twat_cache.paths:get_cache_path:70 - 
Created cache directory: /Users/adam/Library/Caches/twat_cache/twat_cache_
ac031fba
_______________________ test_cache_config_creation _______________________

    def test_cache_config_creation() -> None:
        """Test cache configuration creation."""
        global_config = GlobalConfig()
    
        # Create cache config with some overrides
        cache_config = CacheConfig(
            maxsize=CACHE_CONFIG_MAXSIZE,
            folder_name="test_cache",
        )
    
>       assert cache_config.maxsize == CACHE_CONFIG_MAXSIZE
E       AssertionError: assert None == 200
E        +  where None = CacheConfig(maxsize=200, folder_name='test_cache'
, use_sql=False, preferred_engine=None, cache_type=None).maxsize

tests/test_config.py:183: AssertionError
_______________________ test_cache_config_with_sql _______________________

    def test_cache_config_with_sql() -> None:
        """Test cache configuration with SQL settings."""
        cache_config = CacheConfig(
            maxsize=CUSTOM_CACHE_MAXSIZE,
            folder_name="custom_cache",
            use_sql=True,
            preferred_engine="disk",
        )
    
>       assert cache_config.maxsize == CUSTOM_CACHE_MAXSIZE
E       AssertionError: assert None == 300
E        +  where None = CacheConfig(maxsize=300, folder_name='custom_cach
e', use_sql=True, preferred_engine='disk', cache_type=None).maxsize

tests/test_config.py:197: AssertionError
___________________ test_lru_cache_maxsize_enforcement ___________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x110d54ce0>

    def test_lru_cache_maxsize_enforcement(lru_engine: FunctoolsCacheEngin
e) -> None:
        """Test that LRU cache respects maxsize."""
        # Fill cache to maxsize
        for i in range(10):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == 10
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", 10), 10)
>       assert len(lru_engine._cache) == 10
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x110d54ce0>._cac
he

tests/test_engines.py:194: AssertionError
________________________ test_engine_registration ________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x110
d20980>

    def test_engine_registration(engine_manager: EngineManager) -> None:
        """Test registration of cache engines."""
        # Default engines should be registered
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
>       assert isinstance(engine, CacheEngine)
E       assert False
E        +  where False = isinstance(<twat_cache.engines.functools.Functoo
lsCacheEngine object at 0x110d54f20>, CacheEngine)

tests/test_engines.py:260: AssertionError
_________________________ test_engine_selection __________________________

engine_manager = <twat_cache.engines.manager.EngineManager object at 0x110
d20980>

    def test_engine_selection(engine_manager: EngineManager) -> None:
        """Test selection of appropriate cache engines."""
        # Test default selection (should be LRU)
        config = global_config.get_cache_config()
        engine = engine_manager.get_engine(config)
        assert isinstance(engine, FunctoolsCacheEngine)
    
        # Test disk cache selection
>       config = CacheConfig(folder_name="test_cache")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:298: TypeError
_______________________ test_engine_configuration ________________________

    def test_engine_configuration() -> None:
        """Test engine configuration."""
        # Test maxsize configuration
>       config = CacheConfig(maxsize=100)
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:332: TypeError
________________________ test_unavailable_engine _________________________

    def test_unavailable_engine() -> None:
        """Test handling of unavailable engines."""
        # Test unavailable preferred engine
>       config = CacheConfig(preferred_engine="nonexistent")
E       TypeError: CacheConfig() takes no arguments

tests/test_engines.py:350: TypeError
__________________________ test_engine_caching ___________________________

test_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at
 0x110d57ef0>

    def test_engine_caching(test_engine: BaseCacheEngine[Any, Any]) -> Non
e:
        """Test basic caching functionality of an engine."""
        call_count = 0
    
        def test_func(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
    
        # First call should compute
        assert test_func(TEST_INPUT) == TEST_RESULT
        assert call_count == 1
        assert test_engine.stats["hits"] == 0
    
        # Second call should use cache
        assert test_func(TEST_INPUT) == TEST_RESULT
>       assert call_count == 1
E       assert 2 == 1

tests/test_engines.py:398: AssertionError
____________________________ test_lru_maxsize ____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x110da45f0>

    def test_lru_maxsize(lru_engine: FunctoolsCacheEngine[Any, Any]) -> No
ne:
        """Test LRU cache maxsize enforcement."""
        # Fill cache to maxsize
        for i in range(LRU_CACHE_SIZE):
            lru_engine._set_cached_value(("key", i), i)
    
        assert len(lru_engine._cache) == LRU_CACHE_SIZE
    
        # Add one more, should evict oldest
        lru_engine._set_cached_value(("key", LRU_CACHE_SIZE), LRU_CACHE_SI
ZE)
>       assert len(lru_engine._cache) == LRU_CACHE_SIZE
E       assert 11 == 10
E        +  where 11 = len({'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0,
 '{"args": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"
], "kwargs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...}
)
E        +    where {'{"args": ["(\'key\', 0)"], "kwargs": {}}': 0, '{"arg
s": ["(\'key\', 1)"], "kwargs": {}}': 1, '{"args": ["(\'key\', 10)"], "kwa
rgs": {}}': 10, '{"args": ["(\'key\', 2)"], "kwargs": {}}': 2, ...} = <twa
t_cache.engines.functools.FunctoolsCacheEngine object at 0x110da45f0>._cac
he

tests/test_engines.py:418: AssertionError
_____________________________ test_lru_stats _____________________________

lru_engine = <twat_cache.engines.functools.FunctoolsCacheEngine object at 
0x110da4ef0>

    def test_lru_stats(lru_engine: FunctoolsCacheEngine[Any, Any]) -> None
:
        """Test LRU cache statistics."""
        # Add some items and access them
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some hits
        lru_engine._get_cached_value("key1")
        lru_engine._get_cached_value("key2")
    
        # Some misses
        lru_engine._get_cached_value("key3")
        lru_engine._get_cached_value("key4")
    
        # Check stats
        stats = lru_engine.stats
>       assert stats["hits"] == EXPECTED_CALL_COUNT
E       assert 0 == 2

tests/test_engines.py:452: AssertionError
======================== short test summary info =========================
FAILED tests/test_cache.py::test_cache_settings_validation - AttributeErro
r: 'dict' object has no attribute 'validate'
FAILED tests/test_cache.py::test_cache_clear - assert 1 == 2
FAILED tests/test_cache.py::test_cache_stats - assert 0 >= 2
FAILED tests/test_cache.py::test_kwargs_handling - assert 2 == 1
FAILED tests/test_config.py::test_cache_config_validation - TypeError: Cac
heConfig.validate_maxsize() missing 1 required position...
FAILED tests/test_config.py::test_default_config - AssertionError: assert 
PosixPath('/Users/adam/Library/Caches/twat_cac...
FAILED tests/test_config.py::test_custom_config - AssertionError: assert P
osixPath('cache.log') == 'cache.log'
FAILED tests/test_config.py::test_get_cache_config - AssertionError: asser
t None == 1000
FAILED tests/test_config.py::test_logging_configuration - AssertionError: 
assert not True
FAILED tests/test_config.py::test_cache_config_creation - AssertionError: 
assert None == 200
FAILED tests/test_config.py::test_cache_config_with_sql - AssertionError: 
assert None == 300
FAILED tests/test_engines.py::test_lru_cache_maxsize_enforcement - assert 
11 == 10
FAILED tests/test_engines.py::test_engine_registration - assert False
FAILED tests/test_engines.py::test_engine_selection - TypeError: CacheConf
ig() takes no arguments
FAILED tests/test_engines.py::test_engine_configuration - TypeError: Cache
Config() takes no arguments
FAILED tests/test_engines.py::test_unavailable_engine - TypeError: CacheCo
nfig() takes no arguments
FAILED tests/test_engines.py::test_engine_caching - assert 2 == 1
FAILED tests/test_engines.py::test_lru_maxsize - assert 11 == 10
FAILED tests/test_engines.py::test_lru_stats - assert 0 == 2
ERROR tests/test_engines.py::test_base_engine_initialization
ERROR tests/test_engines.py::test_base_engine_validation
ERROR tests/test_engines.py::test_lru_cache_initialization
ERROR tests/test_engines.py::test_engine_clear
ERROR tests/test_twat_cache.py::test_lru_cache_get_set - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_clear - TypeError: CacheCon
fig() takes no arguments
ERROR tests/test_twat_cache.py::test_lru_cache_maxsize - TypeError: CacheC
onfig() takes no arguments
ERROR tests/test_twat_cache.py::test_disk_cache_persistence - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_joblib_numpy_array - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_klepto_persistence - TypeError: Cache
Config() takes no arguments
ERROR tests/test_twat_cache.py::test_async_cache_operations - TypeError: C
acheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachebox_operations - TypeError: Cach
eConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_cachetools_operations - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_get_set - TypeError: 
CacheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_clear - TypeError: Ca
cheConfig() takes no arguments
ERROR tests/test_twat_cache.py::test_functools_cache_maxsize - TypeError: 
CacheConfig() takes no arguments
================ 19 failed, 22 passed, 16 errors in 0.71s ================

```

---

_****_







I see several issues that need to be fixed:

1. CacheConfig initialization is still not working properly
2. Cache stats are not being tracked correctly
3. LRU cache maxsize enforcement is not working
4. Environment variables are not being handled correctly

Let's fix these issues one by one. First, let's fix the CacheConfig initialization.

---

_****_

Read file: src/twat_cache/types.py

---

_****_







I see the issue. The CacheConfig in types.py is an abstract base class, but we're trying to use it directly. Let's update the CacheConfig class in config.py to properly implement the abstract base class.

---

_****_

```diff
  
  
- class CacheConfig(BaseModel, CacheConfigBase):
+ class CacheConfig(BaseModel):
      """
      Cache configuration model.
          self.validate()
  
+     def __init__(self, **data: Any) -> None:
+         """Initialize the cache configuration."""
+         super().__init__(**data)
+         self.validate()
+ 
  
  class GlobalConfig(BaseSettings):
```

---

_****_







Let me try a different approach. We need to make CacheConfig a proper implementation of CacheConfigBase.

---

_****_

```diff
  
  
- class CacheConfig(BaseModel):
+ class CacheConfig(BaseModel, CacheConfigBase):
      """
      Cache configuration model.
      """
  
-     maxsize: int | None = Field(
+     _maxsize: int | None = Field(
          default=None,
+         alias="maxsize",
          description="Maximum number of items to store in the cache",
      )
-     folder_name: str | None = Field(
+     _folder_name: str | None = Field(
          default=None,
+         alias="folder_name",
          description="Name of the folder to store cache files in",
      )
-     use_sql: bool = Field(
+     _use_sql: bool = Field(
          default=False,
+         alias="use_sql",
          description="Whether to use SQL-based storage",
      )
-     preferred_engine: str | None = Field(
+     _preferred_engine: str | None = Field(
          default=None,
+         alias="preferred_engine",
          description="Preferred cache engine to use",
      )
-     cache_type: CacheType | None = Field(
+     _cache_type: CacheType | None = Field(
          default=None,
+         alias="cache_type",
          description="Type of cache to use (speed, database, filesystem)",
      )
          "from_attributes": True,
          "populate_by_name": True,
-     }
+         "underscore_attrs_are_private": True,
+     }
+ 
+     @property
+     def maxsize(self) -> int | None:
+         """Maximum number of items to store in the cache."""
+         return self._maxsize
+ 
+     @property
+     def folder_name(self) -> str | None:
+         """Name of the folder to store cache files in."""
+         return self._folder_name
+ 
+     @property
+     def use_sql(self) -> bool:
+         """Whether to use SQL-based storage."""
+         return self._use_sql
+ 
+     @property
+     def preferred_engine(self) -> str | None:
+         """Preferred cache engine to use."""
+         return self._preferred_engine
+ 
+     @property
+     def cache_type(self) -> CacheType | None:
+         """Type of cache to use."""
+         return self._cache_type
  
      def validate(self) -> None:
          """Validate all configuration settings."""
-         if self.maxsize is not None:
-             self.validate_maxsize(self.maxsize)
-         if self.folder_name is not None:
-             self.validate_folder_name(self.folder_name)
-         if self.cache_type is not None:
-             self.validate_cache_type(self.cache_type)
+         if self._maxsize is not None:
+             self.validate_maxsize(self._maxsize)
+         if self._folder_name is not None:
+             self.validate_folder_name(self._folder_name)
+         if self._cache_type is not None:
+             self.validate_cache_type(self._cache_type)
  
      @classmethod
-     @field_validator("maxsize")
+     @field_validator("_maxsize")
      def validate_maxsize(cls, v: int | None) -> int | None:
          """Validate maxsize setting."""
  
      @classmethod
-     @field_validator("folder_name")
+     @field_validator("_folder_name")
      def validate_folder_name(cls, v: str | None) -> str | None:
          """Validate folder name setting."""
  
      @classmethod
-     @field_validator("cache_type")
+     @field_validator("_cache_type")
      def validate_cache_type(cls, v: CacheType | None) -> CacheType | None:
          """Validate cache type setting."""
```

---

_****_



I've made several key changes to properly implement the CacheConfigBase abstract base class:

1. Made CacheConfig inherit from both BaseModel and CacheConfigBase
2. Changed field names to use underscores with aliases to maintain the public API
3. Added properties to expose the private fields, matching the abstract base class interface
4. Updated the model_config to handle underscore attributes properly
5. Updated all validators to work with the private field names
6. Added proper type hints and docstrings

Let me check if this resolves the test failures.

---

_****_

```bash
python -m pytest
```

```
/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/.venv/bin/python: No module named pytest

```

---

_****_



I apologize for the error. Let's install pytest first using uv as specified in the instructions.

---

_****_

```bash
uv pip install pytest pytest-asyncio
```

```
Resolved 5 packages in 188ms
Installed 5 packages in 9ms
 + iniconfig==2.0.0
 + packaging==24.2
 + pluggy==1.5.0
 + pytest==8.3.4
 + pytest-asyncio==0.25.3

```

---

_****_



Now let's run the tests again:

---

_****_

```bash
python -m pytest
```

```
/Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plu
gins/repos/twat_cache/.venv/lib/python3.12/site-packages/pytest_asyncio/pl
ugin.py:207: PytestDeprecationWarning: The configuration option "asyncio_d
efault_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture
 caching scope. Future versions of pytest-asyncio will default the loop sc
ope for asynchronous fixtures to function scope. Set the default fixture l
oop scope explicitly in order to avoid unexpected behavior in the future.
Valid fixture loop scopes are: "function", "class", "module", "package", "
session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET
))
========================== test session starts ===========================
platform darwin -- Python 3.12.8, pytest-8.3.4, pluggy-1.5.0 -- /Users/ada
m/Developer/vcs/github.twardoch/pub/twat-packages/_good/twat/plugins/repos
/twat_cache/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/adam/Developer/vcs/github.twardoch/pub/twat-packages/_good
/twat/plugins/repos/twat_cache
configfile: pyproject.toml
testpaths: tests
plugins: asyncio-0.25.3
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None
collected 0 items / 4 errors                                             

================================= ERRORS =================================
__________________ ERROR collecting tests/test_cache.py __________________
ImportError while importing test module '/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_cache/tests/test_
cache.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importli
b/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_cache.py:15: in <module>
    from twat_cache.cache import clear_cache, get_stats
E   ModuleNotFoundError: No module named 'twat_cache'
_________________ ERROR collecting tests/test_config.py __________________
ImportError while importing test module '/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_cache/tests/test_
config.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importli
b/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_config.py:19: in <module>
    from twat_cache.config import CacheConfig, GlobalConfig
E   ModuleNotFoundError: No module named 'twat_cache'
_________________ ERROR collecting tests/test_engines.py _________________
ImportError while importing test module '/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_cache/tests/test_
engines.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importli
b/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_engines.py:24: in <module>
    from twat_cache.engines.base import BaseCacheEngine
E   ModuleNotFoundError: No module named 'twat_cache'
_______________ ERROR collecting tests/test_twat_cache.py ________________
ImportError while importing test module '/Users/adam/Developer/vcs/github.
twardoch/pub/twat-packages/_good/twat/plugins/repos/twat_cache/tests/test_
twat_cache.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importli
b/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_twat_cache.py:20: in <module>
    from twat_cache.engines.functools import FunctoolsCacheEngine
E   ModuleNotFoundError: No module named 'twat_cache'
======================== short test summary info =========================
ERROR tests/test_cache.py
ERROR tests/test_config.py
ERROR tests/test_engines.py
ERROR tests/test_twat_cache.py
!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!
=========================== 4 errors in 0.14s ============================

```

---

_****_





I see the issue now. The package is not installed in development mode, so Python can't find the `twat_cache` module. Let's install it in development mode:

---

_****_

```bash
uv pip install -e .
```

```
Resolved 9 packages in 260ms
Prepared 1 package in 1.00s
Installed 9 packages in 10ms
 + annotated-types==0.7.0
 + loguru==0.7.3
 + platformdirs==4.3.6
 + pydantic==2.10.6
 + pydantic-core==2.27.2
 + pydantic-settings==2.7.1
 + python-dotenv==1.0.1
 + twat-cache==0.1.0 (from file:///Users/adam/Developer/vcs/github.twardoc
h/pub/twat-packages/_good/twat/plugins/repos/twat_cache)
 + typing-extensions==4.12.2

```

---

_****_





---

_**User**_

Read @TODO.md from 2.1. onwards. Rewrite that section, mark what's done, update @LOG.md 

As you develop, run 

```
uv venv; source .venv/bin/activate; uv pip install -e .[all,dev,test]; hatch run lint:fix; hatch test;
```

then continue on what's still TODO


---

_**Assistant**_



---



---

