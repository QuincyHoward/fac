# README 体系维护 Skill

本目录是 FAC 项目级 skill `fac-readme-maintainer` 的人类入口。规则正文见 [`SKILL.md`](SKILL.md)。

## 用途

- 为受管理目录补齐并更新 `README.md`。
- 从底层脚本和源码向上阅读，避免只依据旧文档转述。
- 核查公式与源码对应关系，对未命中公式添加下划线注记。
- 输出目录清单、更新清单、公式核查清单与验证结果。

## 执行入口

- Agent 读取：`skills/fac-readme-maintainer/SKILL.md`
- 详细规则：`references/`
- MCP 服务可通过 `read_skill` 工具读取本 skill。

## 维护结果

每次执行后应更新根 `README.md` 的文档导航，并在报告中列出未解决项。不要在本目录之外新增重复规则。
