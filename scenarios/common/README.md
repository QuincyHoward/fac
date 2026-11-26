# scenarios/common

场景共享工具层，只提供路径、清单、场景模型、表读取与可选绘图能力；不包含物理场景本身。

## 文件

- `paths.py`：场景根与 FAC 根路径，拒绝路径穿越。
- `manifest.py`：JSON 清单读取。
- `scene.py`：`Scene` 数据模型。
- `readers.py`：输出表头部与行读取。
- `plotting.py`：延迟导入 matplotlib 的双列绘图工具。

## 验证

`python ../../scripts/06_scenarios/audit_scenarios.py` 检查场景清单与锚点；绘图依赖缺失时由 `plotting.py` 给出安装提示。

## 导航

父级 [`../README.md`](../README.md)；核心 [`../core/README.md`](../core/README.md)。
