# Commands to Fix

## 1. Make target: test

**Command:** `make test`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 3.42s

**Output:**
```
poetry run pytest
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/tom/github/wronai/mdiss
configfile: pyproject.toml
testpaths: tests
plugins: cov-4.1.0, mock-3.14.1
collected 72 items

tests/test_analyzer.py .FFFFF.FFFFFF                                     [ 18%]
tests/test_cli.py ..F....F.F...F......FF.                                [ 50%]
tests/test_github_client.py F..........F.FF......
```

**Error Output:**
```
make: *** [Makefile:15: test] Error 1

```

**Metadata:**
- **target:** test
- **original_command:** make test

---

## 2. Make target: test-verbose

**Command:** `make test-verbose`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 3.67s

**Output:**
```
poetry run pytest -v
============================= test session starts ==============================
platform linux -- Python 3.12.9, pytest-7.4.4, pluggy-1.6.0 -- /home/tom/.cache/pypoetry/virtualenvs/mdiss-VgxEfGFg-py3.12/bin/python
cachedir: .pytest_cache
rootdir: /home/tom/github/wronai/mdiss
configfile: pyproject.toml
testpaths: tests
plugins: cov-4.1.0, mock-3.14.1
collecting ... collected 72 items

tests/test_analyzer.py::TestErrorAnalyzer::test_analyze_poetry_lock_issue PASSED [  1%]
te...
```

**Error Output:**
```
make: *** [Makefile:18: test-verbose] Error 1

```

**Metadata:**
- **target:** test-verbose
- **original_command:** make test-verbose

---
