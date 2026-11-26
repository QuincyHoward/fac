# fac_demo 场景区

按物理原型组织的一键执行、产物阅读理解与绘图演示。每个子目录只描述一种原型，不绑定单一具体算例。

## 1. 文件树

```text
fac_demo/
├── cases/            # 物理原型场景
├── outputs/          # 输出产物说明与占位
├── plots/            # 图像产物说明与占位
├── scene_manifest.json
├── run_scene.py      # list / describe / run 入口
└── README.md
```

## 2. 常用命令

```bash
python run_scene.py list
python run_scene.py describe --name structure_tr
python run_scene.py run --name structure_tr --dry-run
python run_scene.py anchors
```

## 3. 场景目录约定

每个场景目录至少包含：

- `README.md`：物理原型、输入、输出、注意事项。
- `scene.json`：`name`、`archetype`、`description`、`entry`。
- `run.py`：一键执行或 dry-run 说明入口。

可选：`explain.py`（输出表阅读理解）、`plot.py`（绘图）。

## 4. 输出与绘图

实际运行产物放在 `outputs/`；图像放在 `plots/`。场景目录移动后通过清单与锚点重新发现，不修改 Python 代码。

## 5. 导航

父级 [`../README.md`](../README.md)；脚本 [`../../scripts/README.md`](../../scripts/README.md)。
