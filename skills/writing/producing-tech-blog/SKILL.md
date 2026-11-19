---
name: producing-tech-blog
description: 将已有 Markdown 技术文章转换为适合微信公众号的内联 CSS HTML，并检查内容保真与排版。适用于已有正文只需排版、生成微信 HTML；不负责重新选题、源码研究或重写正文，内容写作使用 wechat-tech-article。
---

# Producing Tech Blog — 微信 HTML 排版

## 输入与边界

输入是已确认的 Markdown 正文、输出位置及可选项目排版约定。Markdown 是内容源，HTML 是派生产物。缺少正文时先获取正文或转入 technical-writing 工作流，不自行补写文章。

按项目说明查找排版约定；没有约定时使用 [微信样式](wechat-styles.md)，不要求先创建配置文件。[项目约定模板](project-conventions.template.md) 仅在维护系列文章确有需要时使用。

## 转换流程

1. 读取全文，盘点标题、段落、代码、图、表格、公式、图片与引用。确认输出路径，保留源稿及已有用户文件。
2. 逐元素转换为 HTML，按微信样式添加内联 CSS。转义正文与代码中的 HTML 特殊字符；禁止将输入中的脚本或事件处理属性带入成品。
3. 保留事实、数值、单位、术语、代码、链接目标和不确定性限定。不得重做研究、重排论证、增加案例或静默删减内容。发现技术疑点列为待确认项。
4. 代码按完整语义展示；过长时优先调整展示方式，需要拆分或省略时保留完整源稿并说明。图使用等宽字体并检查窄屏；表格转为列表时保留行列对应关系。
5. 图片保留来源与说明；未上传微信的图片记录待上传项。无法支持的公式或图示明确标注，不将空占位称为转换完成。

## 可选工具（scripts/）

仅在当前环境有 Python 3.8+ 时使用；脚本不可用不阻塞手工转换。

```bash
python3 scripts/md2wx.py article.md -o article.html --accent "#1677FF" --font-size 16
python3 scripts/blog_lint.py article.md --deny deny-words.txt
```

- `md2wx.py` 生成内联 CSS HTML，并在输出旁写 `article.report.json`；只做排版转换，不改写正文。
- `blog_lint.py` 做编码、敏感词、结构与发布前体检；P0/P1 必须修，P2 按需处理。
- 工具是辅助证据，不是预览证明；微信客户端预览仍需单独记录。

## 验收与交付

- 对照源稿检查标题、段落、数字、代码、图表信息及引用完整性，确认转义正确、标签闭合、CSS 内联且无外部脚本依赖。
- 技术审校逐条过 `references/TECH_REVIEW_CHECKLIST.md`；配图与截图脱敏参照 `references/BLOG_IMAGE_GUIDE.md`。
- 有浏览器时检查窄屏、长代码与图表；实际微信客户端预览单独记录。静态检查不能证明微信显示正常。
- 交付源稿路径、HTML 路径和检查结果；区分已验证、待人工预览、待上传和受阻事项。
- 无法生成或检查某元素时交付已有结果与具体缺口，不声称全部通过。
- 通用证据分级、输入不足与交付复用规则见 `references/shared-method.md`。

完整研究与写作由 technical-writing 工作流编排；内容改写使用 wechat-tech-article，语言润色按需使用 humanizer-zh。
