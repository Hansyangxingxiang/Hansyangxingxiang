# Workflow: technical-writing

## 目的

把技术资料 / 研究 / 排障 / 方案内容，重组成面向读者的技术文章，去 AI 味，并排版成微信 HTML。

## 适用场景

- 公众号技术文章
- 技术博客
- 系列文章（需结构一致性）

## 阶段流水线

```
技术资料
  → 内容整理
  → wechat-tech-article（选题 / 结构 / 草稿）
  → humanizer-zh（去 AI 味）
  → producing-tech-blog（排版成微信 HTML）
```

## 每阶段用到的 Skill

| 阶段 | Skill |
|---|---|
| 选题 / 定标题 / 组织结构 / 草稿 | `wechat-tech-article` |
| 去 AI 味 | `humanizer-zh` |
| 排版成微信 HTML | `producing-tech-blog` |

## 产出物

- 内容草稿（见 `templates/technical-article.md`）
- 去 AI 味后的正文
- 微信 HTML（`.md` + 内联 CSS 的 `.html`）

## 检查清单

- [ ] 问题驱动开头，不写"什么是 X"式科普
- [ ] 事实 / 分析 / 观点三分离
- [ ] 英文技术词保留原文
- [ ] 去 AI 味（无夸大象征 / 宣传语 / 三段式 / 破折号滥用）
- [ ] 排版符合微信规范（内联 CSS，无外部依赖）
- [ ] 系列文章结构一致
