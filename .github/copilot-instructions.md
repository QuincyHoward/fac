# VS Code Copilot 入口

在 `{fac/}` 项目中，先读取 [`AGENTS.md`](../AGENTS.md)，再按任务加载对应 skill：

- 构建与首次上手：`skills/fac-onboarding/SKILL.md`
- demo 工作流：`skills/fac-demo-workflow/SKILL.md`
- demo 排障：`skills/fac-demo-troubleshooting/SKILL.md`
- 源码导航：`skills/fac-code-navigation/SKILL.md`
- README 体系维护：`skills/fac-readme-maintainer/SKILL.md`

凭证管理入口见 `scripts/credentials/manage.py`，默认 namespace 为 `specx`，输出默认脱敏。

本文件不复制规则正文；以 `AGENTS.md` 与各 `SKILL.md` 为准。构建与运行使用独立可写工作目录占位符 `<WORK_ROOT>`，不要写死具体路径。
