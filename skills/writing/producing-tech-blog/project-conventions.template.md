# [Project Name] Blog Conventions

Copy this file into the project (e.g. `docs/blog/blog-conventions.md` or the project memory dir) and fill in the brackets. One filled instance per project.

## Series Outline

| # | Title | Status | Source material |
|---|-------|--------|-----------------|
| 1 | ... | DONE/TODO | path/to/source |
| 2 | ... | TODO | path/to/source |

## Section Template

1. Hook (X-Y words): concrete scene, throw a question
2. Background (X-Y words): industry contrast + this project's constraints
3. Core Design (X-Y words): diagram + short code, WHY first
4. Pitfalls (X-Y words): real bugs + source evidence
5. Summary (X-Y words): recap + tease next article

## Word Count

Target: X-Y words per article

## Diagram Style

- Format: ASCII art in fenced code blocks
- Caption: `**图 N：description**` below the code block
- Box-drawing chars: ─│├└┌┐

## Code Blocks

- Prefer concise, semantically complete excerpts; preserve full code and validate mobile readability
- Line reference format: `file.cpp:LINE`
- Complex logic → pseudocode

## Terminology

| 术语 | Standard usage |
|------|---------------|
| ... | ... |

## Source Code Roots

- `path/to/main/` — one-line description
- `path/to/management/` — one-line description

## Notes Location

- MEMORY.md: /path/to/memory/MEMORY.md
- Blog dir: docs/blog/
