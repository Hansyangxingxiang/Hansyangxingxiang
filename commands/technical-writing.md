---
description: 技术写作：原理文章/公众号表达/润色/微信 HTML 排版，按需进入各阶段
argument-hint: <写作任务、主题或待处理文本>
---

按 technical-writing 工作流处理下面的写作任务：

$ARGUMENTS

执行步骤：

1. 读取 `~/.claude/workflows/technical-writing/WORKFLOW.md`；该文件不存在时，读取本命令来源仓库的 `workflows/technical-writing/WORKFLOW.md`。
2. 按目标选择入口：
   - 项目机制、原理系列、技术评审：`writing-project-principles`
   - 公众号选题与读者表达：`wechat-tech-article`
   - 仅语言润色：`humanizer-zh`
   - 仅微信 HTML 排版：`producing-tech-blog`
   - NeonSAN 专属原理文档规范：`writing-neonsan-internals`（personal-notes 仓库维护）
3. 只执行用户范围要求的阶段，不为凑齐流程生成无关文件；原理内容由 `writing-project-principles` 负责机制与证据，表达调整保留事实、限定与作者声音。
4. 区分已完成、待人工预览与未执行项；微信客户端预览不能由静态检查替代。
5. 交付源稿路径、派生 HTML 路径（如要求）与检查状态；不自动发布。
