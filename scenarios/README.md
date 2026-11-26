# FAC 场景系统

本目录只负责**物理场景的创建、发现与整理**，不承载通用工具实现；通用脚本在 [`../scripts/`](../scripts/README.md)。

## 1. 设计原则

- **位置优先**：场景身份由目录中的 `scene.json` 与相对位置派生，整理/移动目录不需要改 Python 代码。
- **自包含**：每个场景目录至少包含 `README.md`、`scene.json`、`run.py`。
- **相对锚点**：跨场景资源通过 `_scene_anchors.json` 与相对路径发现，不写死机器路径。
- **场景层只管物理**：场景描述、输入参数、输出解释与绘图入口留在场景目录；运行和审计工具下沉到 `common/`、`core/`。
- **可手动整理**：可直接剪切粘贴场景目录；用 `python ../scripts/06_scenarios/audit_scenarios.py` 验证。

## 2. 目录总览

```text
scenarios/
├── common/       # 场景共享工具：路径、清单、读取、绘图
├── core/         # 发现、基础运行、锚点解析
├── run/          # local/wsl/hpc-remote/hpc-insitu 仿真接口
├── fac_demo/     # 按物理原型组织的演示场景
└── _scene_anchors.json
```

## 3. 运行与审计

```bash
python fac_demo/run_scene.py list
python fac_demo/run_scene.py describe --name FeL_single_node
python fac_demo/run_scene.py run --name FeL_single_node --mode hpc-remote --cores auto -n
python -m scenarios.run.hpc status --job <ID>
python ../scripts/06_scenarios/audit_scenarios.py
```

## 4. 新建场景

1. 复制最接近的场景目录。
2. 修改 `scene.json` 的 `name`、`archetype`、`description` 与 `entry`。
3. 在 `run.py` 中只写该物理场景的执行/说明逻辑。
4. 补 `README.md`、`explain.py`、`plot.py`（按需）。
5. 运行审计脚本确认清单和锚点可解析。

## 5. 导航

父级 [`../README.md`](../README.md)；上下文 [`../AGENTS.md`](../AGENTS.md)；脚本 [`../scripts/README.md`](../scripts/README.md)；演示 [`fac_demo/README.md`](fac_demo/README.md)。
