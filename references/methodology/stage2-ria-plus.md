# 阶段 2 — RIA++ 构造 skill

对每个通过单元，按 `references/templates/SKILL.md.template` 填充六段。

## 六段定义

- **R（Reading）原文引用**：≤150 字/段（英文 ≤100 词/段），必须来自原文，标注位置。
- **I（Interpretation）解读**：用自己的话重写方法论骨架，避免照搬译本；突出机制与因果。
- **A1（Past Application）过往应用**：书中/视频中作者亲自用过的案例，证明有效。
- **A2（Future Trigger）未来触发 ★**：用户在什么情境下会需要这个 → 即 skill 的 `description` 字段，必须含明确 trigger 条件（如「当用户要写卖点文案时」）。
- **E（Execution）可执行步骤**：1-2-3 步，具体可操作，最好带检查点。
- **B（Boundary）边界**：何时不适用 / 来自阶段 0 批判的作者盲点 / 常见误用。

## 细则

- A2「与相邻 skill 的区分」先写初稿（基于 verified.md 的单元列表），阶段 3 建立链接后回填定稿。
- `description` 字段严禁写成「一个关于 X 的 skill」——必须写清触发条件与产出。
- 原文引用超长则截断并注明「…（略）」，不可整段搬运。
- 每个 skill 独立成目录 `<skill-slug>/SKILL.md`，slug 用 kebab-case、有业务语义（如 `headline-formula`）。

## 质量自检

- 六段是否齐全？缺一段即不合格。
- R 段是否标注原文位置、是否超限？
- A2 是否可被 Agent 直接用于路由判断？
