# FAC 项目级 Skills

本目录是 FAC 所有 Agent skill 的唯一事实源，供 Codex、OpenCode、Cursor、Zed、Warp、Amp、Jules、VS Code、Claude Code、Workbuddy、CodeBuddy 等 Agent 直接读取。

## 1. 定位与职责

- `SKILL.md` 给 Agent 提供触发规则与工作流。
- `README.md` 给人类提供入口说明。
- `references/` 承载详细清单、错误库、模板与校验规则。

## 2. 当前 Skills

| Skill | 用途 |
|---|---|
| [`fac-onboarding`](fac-onboarding/SKILL.md) | 首次上手、重新构建、并行构建、导入与冒烟检查 |
| [`fac-demo-workflow`](fac-demo-workflow/SKILL.md) | demo 工作流、原型分类、依赖与回归方式 |
| [`fac-demo-troubleshooting`](fac-demo-troubleshooting/SKILL.md) | 构建、运行、比对、崩溃、长耗时与单位问题排障 |
| [`fac-code-navigation`](fac-code-navigation/SKILL.md) | FAC 概述、模块地图、功能到源码映射、API 调用链 |
| [`fac-readme-maintainer`](fac-readme-maintainer/SKILL.md) | 自底向上维护 README 与公式注记 |

## 3. 输入/输出与验证

- 输入：项目 README、源码、脚本、场景与用户任务描述。
- 输出：更新后的 README、审计报告、下一步建议。
- 验证：所有 skill 必须通过 `quick_validate.py`；`AGENTS.md` 入口必须指向本目录。

## 4. 已知限制

Skill 不替代源码事实；公式与调用链结论仍需源码/输出表证据支撑。不要在本目录外复制规则正文。

## 5. 导航

父级 [`../README.md`](../README.md)；上下文协议 [`../AGENTS.md`](../AGENTS.md)；MCP 只读入口 [`../mcp_server.py`](../mcp_server.py)。
