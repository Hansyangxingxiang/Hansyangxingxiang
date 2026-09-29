---
name: producing-tech-blog
description: Use when writing a technical blog article needing source code analysis, architecture diagrams, and WeChat-compatible HTML output — for multi-article series requiring structural consistency
---

# Producing Tech Blog

## Overview

4-stage pipeline: source analysis → diagram design → writing → dual-output formatting. Project-specific conventions (series outline, section template, terminology, source roots) live in a project-conventions file, NOT in this skill — swap projects by swapping that file.

## When to Use

- Writing a technical blog that references source code
- Producing WeChat公众号 articles (or any platform needing inline-CSS HTML)
- Multi-article series that must stay structurally consistent

## Prerequisites

Locate the project's blog conventions file (e.g. `docs/blog/blog-conventions.md`, or `blog-series.md` in the project memory dir). It defines: series outline, section template, word count, diagram style, terminology, source roots. None? Scaffold from `project-conventions.template.md` first.

## Phase 1: Source Analysis

1. Grep for key structs/functions by name — never trust memory for line numbers
2. Read core structures/functions, record exact `file:line` references
3. Trace data flow / call chains to find the article's spine
4. MEMORY.md is a lead only — **verify every conclusion against current source** (lines drift)
5. Output: "source map" — `{concept, file:line, one-line summary}` list

## Phase 2: Diagram Design

1. List 3-5 diagrams (one per major concept)
2. ASCII art in fenced code blocks (box-drawing chars per project conventions)
3. Each diagram MUST be **self-contained** — readable without surrounding prose
4. Types: architecture overview, data-flow sequence, data structure, state machine, comparison table
5. Caption: `**图 N：description**` below the code block

## Phase 3: Writing

1. Follow the project's section template (NeonSAN: hook 300-500 / background 500-800 / core design 1500-2500 / pitfalls 500-800 / summary 200-400)
2. Code blocks ≤15 lines; pseudocode for complex logic; every reference carries `file:line`
3. Hook: concrete scene + question; never start with "什么是 X"
4. Core design: diagram + short code, explain WHY not WHAT
5. Pitfalls: real bugs/gotchas with source evidence

## Phase 4: Dual-Output Formatting

**Markdown (.md) — source of truth:** save to the project blog dir (e.g. `docs/blog/article-NN-*.md`); ASCII diagrams in fenced code blocks; standard markdown.

**WeChat HTML (.html) — publish version:** apply inline CSS from `wechat-styles.md` (WeChat strips `<style>` — every style must be inline). Code blocks: `<pre style="...">` + monospace. ASCII diagrams: `<pre>` blocks (monospace preserves alignment). Images: placeholder comments (manual upload). Self-check: no markdown residue, code blocks <20 lines (WeChat truncates), diagrams aligned.

## Checklist

- [ ] All `file:line` references re-verified against current source
- [ ] 3-5 diagrams, each self-contained
- [ ] Code blocks ≤15 lines; word count in project target range
- [ ] Section template followed
- [ ] `.md` saved to blog dir; `.html` generated via wechat-styles
- [ ] WeChat preview: code blocks render, diagrams aligned, no markdown residue

## Common Mistakes

- **Line drift unchecked** — re-verify before publishing
- **Diagram not self-contained** — needs surrounding prose to be readable
- **Code block >15 lines** — WeChat truncates, readers skim
- **Writing WHAT not WHY** — reader can read source for WHAT
- **Trusting MEMORY.md line numbers verbatim** — always cross-check source
