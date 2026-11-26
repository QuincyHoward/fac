# R 矩阵原型

演示两阶段 R 矩阵工作流。

- 输入：靶态、关联态、径向网格、两区边界。
- 核心 API：`RMatrixTargets`、`RMatrixBoundary`、`RMatrixBasis`、`RMatrixSurface`、`RMatrixCE`。
- 输出：`.b*`、`.d*`、`r1.d`。
- 验证：前置文件完整性、能量网格、碰撞强度正值性。
- 注意：两阶段顺序不可颠倒；线程数由脚本决定；无官方基准时不能写“自动回归通过”。

导航：[`../../README.md`](../../README.md)。
