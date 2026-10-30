# WeChat Inline Styles Reference

WeChat strips `<style>` tags and external CSS, so every style must be inlined via `style="..."` on each element. Use this table when converting `.md` to WeChat `.html`.

## Element Style Map

| Element | HTML | Inline style |
|---------|------|--------------|
| H1 | `<h1>` | `style="font-size:22px;font-weight:bold;color:#333;border-bottom:2px solid #333;padding-bottom:8px;margin:24px 0 16px;"` |
| H2 | `<h2>` | `style="font-size:18px;font-weight:bold;color:#333;border-left:4px solid #2c7be5;padding-left:12px;margin:20px 0 12px;"` |
| H3 | `<h3>` | `style="font-size:16px;font-weight:bold;color:#2c7be5;margin:16px 0 8px;"` |
| Paragraph | `<p>` | `style="font-size:15px;line-height:1.75;color:#3a3a3a;margin:0 0 16px;"` |
| Code block | `<pre><code>` | `<pre style="background:#f6f8fa;padding:12px;border-radius:4px;overflow-x:auto;font-size:13px;line-height:1.5;margin:0 0 16px;"><code style="font-family:Menlo,Monaco,Consolas,monospace;color:#333;">` |
| Inline code | `<code>` | `style="background:#f6f8fa;padding:2px 6px;border-radius:3px;font-family:monospace;font-size:13px;color:#d6336c;"` |
| Blockquote | `<blockquote>` | `style="border-left:4px solid #2c7be5;padding:8px 12px;margin:16px 0;background:#f6f8fa;color:#666;font-size:14px;"` |
| List | `<ul>/<ol>` | `style="font-size:15px;line-height:1.75;color:#3a3a3a;margin:0 0 16px 20px;"` |
| ASCII diagram | `<pre>` | `style="background:#f6f8fa;padding:12px;border-radius:4px;overflow-x:auto;font-size:13px;line-height:1.4;font-family:Menlo,Monaco,Consolas,monospace;color:#333;margin:0 0 8px;"` |
| Image placeholder | `<!-- -->` | `<!-- 图片：description，上传后替换 -->` |

## Generation Rules

1. Convert each `.md` element one-by-one, applying the table's style
2. ASCII diagram code blocks use the "ASCII diagram" row (tighter `line-height:1.4`)
3. Prefer concise, semantically complete code excerpts. Preserve full source; do not silently truncate code to meet a line count.
4. No `<img>` directly — use placeholder comments; upload manually when publishing
5. Output a full HTML document for local inspection. The WeChat paste/import path and resulting rendering require client preview.

## WeChat Gotchas

- Long code blocks may be difficult to read on mobile; verify the actual client rendering before choosing a display adjustment
- ASCII diagrams MUST use monospace + no-wrap, or alignment breaks
- WeChat does not render `<table>` styles directly — convert tables to HTML lists or screenshots
- In-body links are not clickable (only the 文末"阅读原文" link jumps) — put important links at the end
