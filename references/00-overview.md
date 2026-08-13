# RIA-TV++ 方法论总览

cangjie-distiller 把长内容变成一组可执行 skill 的完整流水线。核心思想是「蒸馏」而非「总结」：

- **总结**是压缩：把 300 页书压成 10 页笔记，目标是「让人快速读懂」，产出静态文字。
- **蒸馏**是工具化：不仅抽取方法论本身，还显式标注「何时触发 / 怎么执行 / 何时不适用」，产出能被 Agent 在真实场景调用的技能单元。

## 七个阶段

| 阶段 | 名称 | 产出 |
|------|------|------|
| 0 | Adler 整书理解 | BOOK_OVERVIEW.md |
| 1 | 5 路并行提取 | candidates/ 候选单元池 |
| 1.5 | 三重验证筛选 | verified.md + rejected/ |
| 2 | RIA++ 构造 | 每个 skill 的 SKILL.md |
| 3 | Zettelkasten 链接 | INDEX.md + GLOSSARY.md |
| 4 | 压力测试 | test-prompts.json + test-results.md |
| 5 | 交付 | DIGEST.md + 安装到用户技能目录 |

## 命名拆解

- **RIA**：赵周《这样读书就够了》便签拆书法 — Reading（原文）/ Interpretation（解读）/ Appropriation（内化应用）
- **TV**：Triple Verification 三重验证（跨域 / 预测力 / 独特性）
- **++**：面向 Agent 执行的扩展 — E（Execution 可执行步骤）+ B（Boundary 边界与盲点）

## 通过率预期

三重验证通过率通常只有 25%–50%。宁少做几个，也要保证每个 skill 真能帮上忙。被淘汰的单元进 `rejected/` 保留审计轨迹，允许用户事后捞回。

## 断点续跑

开始前检查 `<slug>/PIPELINE_STATE.md`；存在则从记录阶段续跑，不从头重来。每完成一阶段更新该文件。
