# 阶段 5 — 交付

## 1. DIGEST.md 精华长文

按 `references/templates/DIGEST.md` 生成面向读者的精华长文：满足「不读全书、只看这篇就够」的需求。
包含：核心主张、方法论地图（链接到各 skill）、最值得立刻用的 3-5 条、使用须知。

## 2. 安装到用户技能目录

通过测试的 skill 复制/软链到 WorkBuddy 用户技能目录：
```
<USER_SKILLS_DIR>/<slug>-<skill-slug>\
```
每个子目录含 `SKILL.md`（可加 `test-prompts.json`）。**没有这一步，产出的 skill 无法被真正调用。**

询问用户安装位置：
- 用户级：`~/.workbuddy/skills/`（全局可用）
- 仅留存产物包：不安装，留在 `./distilled\<slug>\`

## 3. 收尾

- 更新 `PIPELINE_STATE.md` 标记全部阶段完成。
- 告知用户：「已完成，可继续迭代（如新增内容、用 darwin 类机制进化）。」
- 把本次蒸馏发现的新的判据/纠词/压力测试先例，追加进 `knowledge/registry.json`（含 last_verified）。
