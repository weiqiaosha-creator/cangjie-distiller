# 阶段 1 — 5 路并行提取

用 **Agent 工具**一次发起 5 个 sub-agent，分别加载 `references/extractors/` 下的 5 个 prompt：

| extractor | 文件 | 产出单元类型 |
|-----------|------|--------------|
| 框架提取器 | framework-extractor.md | 决策框架 / 思维模型 |
| 原则提取器 | principle-extractor.md | 原则 / 清单 / 规则 |
| 案例提取器 | case-extractor.md | 作者亲自用过的实例 |
| 反例提取器 | counter-example-extractor.md | 书中警告的失败模式 |
| 术语提取器 | glossary-extractor.md | 关键概念词典 |

## 调度方式

- 每个 sub-agent 独立读原文、独立提取，输出到 `candidates/<type>.md`（统一格式：每条单元含「原文位置 + 单元名称 + 一句话摘要 + 为何可复用」）。
- 一次消息内并发 5 个 Agent 调用；subagent_type 用 `general-purpose`。
- Prompt 中须写明：把结果通过文件写回 `candidates/<type>.md`，并简短回传摘要。

## 长文本分块策略

单 sub-agent 上下文装不下整本时：
1. 按阶段 0 的骨架把原文切成 N 块（每块带块号与位置标注）。
2. 每个提取器对每块各跑一次（同 prompt，不同块）。
3. 主流程归并各块候选，去重（同方法论不同表述合并）。

## 降级方案

当前环境不支持并行 sub-agent 时，串行执行同一组 5 个 prompt，产出格式不变。

## 覆盖率检查（逐块回执，移植自 yizhan-shendeng v2）

长文本下 sub-agent 极易只读前段就产出，且不自知。用逐块回执对抗：

1. 每块原文切分时已连续编号（从 1 开始），总块数是覆盖率基准。
2. 每路 extractor 输出须含**逐块回执**：对每批每块各写一行「第 X 块：找到 N 条」或「第 X 块：无」。
3. 任一区块缺回执 → 仅针对漏块**补派一次**该路（任务描述写明上次漏掉哪几块），不整批重来（整批重来会大量重复且添乱去重）。
4. 补派最多一次；第二次仍不全则接受现状，在 `PIPELINE_STATE.md` 记「第 X 批第 Y 路覆盖不全」，最终清单告知用户。
5. 候选**全部落盘后**再更新 `PIPELINE_STATE.md` 的批进度；顺序反了，中断会误判本批已完成。
