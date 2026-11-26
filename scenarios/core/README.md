# scenarios/core

场景发现、运行与锚点解析层。场景目录可通过文件管理器移动；本层通过 `scene.json` 与 `_scene_anchors.json` 解析，不依赖位置硬编码。

## 文件

- `discovery.py`：递归发现 `scene.json`。
- `scene.py`（由 common 提供）：场景模型。
- `runner.py`：以 dry-run 优先的场景执行器。
- `anchors.py`：逻辑锚点解析与路径穿越检查。

## 验证

`python fac_demo/run_scene.py list` 与 `python ../../scripts/06_scenarios/audit_scenarios.py`。

## 导航

父级 [`../README.md`](../README.md)；公共工具 [`../common/README.md`](../common/README.md)。
