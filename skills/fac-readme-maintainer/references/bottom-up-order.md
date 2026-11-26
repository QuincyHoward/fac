# 自底向上阅读与更新顺序

严格按以下顺序推进。读取可并行，写入同一 README 必须串行；父目录更新必须晚于子目录。

## 1. 数值支撑库

`blas/`、`lapack/`、`minpack/`、`quadpack/`、`toms/`、`ode/`、`mpfun/`

关注：数值例程职责、输入参数、输出语义、被哪些物理库调用。

## 2. 物理支撑库

`coul/`、`modqed/`、`ionis/`

关注：特殊函数、连续态、QED 与电离平衡拟合的物理意义及调用入口。

## 3. 核心库

`faclib/`

关注：结构、跃迁、CE、CI、PI/RR、AI/DR、CRM、谱、偏振、R 矩阵、数据表输出器。

## 4. 接口层

`python/`、`sfac/`

关注：PFAC 与 SFAC 命令到核心函数的映射、读取器、典型调用顺序。

## 5. 示例与文档

`demo/`、`doc/`

关注：输入输出依赖、回归方式、输出表单位、常见问题；`demo/` 的规则应抽象到原型层级。

## 6. 新增工程目录

`scripts/`、`scenarios/`、`skills/`

关注：工具职责、场景发现、锚点解析、skill 触发规则与 README 入口。

## 7. 根目录

`README.md`、`AGENTS.md`、`DEPENDENCIES.md` 及其他适配入口。

关注：总览、导航、依赖、入口一致性；只在所有子目录完成后更新。

## 目录覆盖规则

- 每个受管理目录必须有一个 `README.md`。
- skill 目录同时保留 `SKILL.md` 与 `README.md`，前者给 Agent，后者给人类。
- 场景目录至少包含 `README.md`、`scene.json`、`run.py`。

## 输出顺序

维护报告按上述顺序排列，便于发现哪一层仍未完成。
