# 阶段 4 — 压力测试

验证每个 skill 是否真能在真实场景被正确触发、不被误用。

## 测试集构造

每个 skill 写 5–10 条 `test-prompts.json`，至少包含三类：
1. **应调用（positive）**：明确匹配该 skill 触发条件的真实问法。
2. **不应调用（decoy 诱饵）**：表面相似但不属于本 skill 的场景。诱饵分两层：
   - **同源混淆**：至少 1 条是「应触发同包另一个 skill」的跨 skill 混淆测试（检验 description 区分度）。
   - **宿主混淆**：至少 1 条是「应由助手通用能力处理、不应调任何本包 skill」的场景。
3. **边界模糊（borderline）**：接近但不完全满足触发条件，检验 B 段边界是否写清。

### 自触发必考题（移植自 yizhan-sheng v2）

测试集必含一题，且**不许省**：
> 帮我把这本书蒸馏成技能

正确判定：触发 **cangjie-distiller 自身**，而非任一新产出的 skill。
风险：蒸馏一本讲读书 / 学习 / 信息处理的内容时，产出的 skill（如「快速读懂一本书」）极易抢走本技能 trigger；一旦抢走，用户再也无法蒸馏任何东西（工具被自己产物顶掉）。答错就改那个新 skill 的 description，明确写「想把一本书做成技能包，不要用这个技能」，然后**重测全部题目**。最多两轮，两轮后仍错的不删，但在其 SKILL.md 开头加标注，并在最终清单点名。

## 执行

- 优先用独立 sub-agent 盲测每条 prompt（不给它答案，让它仅凭 skill 的 description + R/I/A2 判断「应调/不应调/边界」）。
- 主流程对照预期统计：通过率、误调（把诱饵判成应调）、漏调（把应调判成不应调）。
- **未过的回炉重做阶段 2**（补强 description 触发条件 / A2 区分 / B 边界），不做表面修补。

## 记录

每个 skill 的测试结果写入 `<skill-slug>/test-results.md`：通过率、失败 case 分析、回炉动作。

## test-prompts.json 格式

见 `references/templates/test-prompts.json`。兼容 darwin-skill 进化格式。
