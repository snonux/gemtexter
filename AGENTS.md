# AGENTS.md

## Build, Lint, and Test

- **Build/generate:** `./gemtexter --generate`
- **Publish:** `./gemtexter --publish`
- **Run all tests:** `./gemtexter --test`
- **Lint (ShellCheck):** `shellcheck --external-sources --check-sourced lib/*.sh ./gemtexter`
- **Run a single test:** Edit `lib/assert.source.sh` or relevant test function, then run `./gemtexter --test`

## Code Style Guidelines

- **Shell:** Bash 5.x+ only. Use `#!/usr/bin/env bash` shebang.
- **Formatting:** 2 spaces, no tabs. Max line length: 80 chars.
- **Imports:** Source libraries with `.sh` extension, not executable.
- **Naming:** Functions/variables: `lower_case`, constants: `ALL_CAPS`.
- **Functions:** Use `package::function()` for libraries. Add header comments for non-trivial functions.
- **Quoting:** Always quote variables, command substitutions, and paths.
- **Error handling:** Use `set -euf -o pipefail`. Check all command return values.
- **Testing:** Use `assert::` functions for unit tests.
- **Linting:** Fix all ShellCheck warnings except those excluded in `assert::shellcheck`.
- **Consistency:** Follow [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) and [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki).

