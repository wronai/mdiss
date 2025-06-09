# Commands to Fix

## 1. Make target: install

**Command:** `make install`
**Source:** /home/tom/github/wronai/domd/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** 2
**Execution Time:** 1.47s

**Output:**
```
make[1]: Entering directory '/home/tom/github/wronai/domd'
poetry install
Installing dependencies from lock file
make[1]: Leaving directory '/home/tom/github/wronai/domd'
```

**Error Output:**
```
pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock` to fix the lock file.
make[1]: *** [Makefile:15: install] Error 1
```

**Metadata:**
- **target:** install
- **original_command:** make install

---

## 2. NPM script: test

**Command:** `npm run test`
**Source:** /home/tom/github/wronai/domd/examples/javascript/package.json
**Type:** npm_script
**Status:** ❌ Failed
**Return Code:** 254
**Execution Time:** 2.79s

**Output:**
```
```

**Error Output:**
```
npm error code ENOENT
npm error syscall open
npm error path /home/tom/github/wronai/domd/package.json
npm error errno -2
npm error enoent Could not read package.json: Error: ENOENT: no such file or directory, open '/home/tom/github/wronai/domd/package.json'
```

**Metadata:**
- **script_name:** test
- **script_command:** echo test

---

## 3. Make target: timeout-test

**Command:** `make timeout-test`
**Source:** /home/tom/github/wronai/domd/Makefile
**Type:** make_target
**Status:** ❌ Failed
**Return Code:** -1
**Execution Time:** 60.00s
**Error:** Command timed out after 60 seconds

**Output:**
```
Starting long running process...
```

**Error Output:**
```
Process killed due to timeout
```

**Metadata:**
- **target:** timeout-test
- **original_command:** make timeout-test

---