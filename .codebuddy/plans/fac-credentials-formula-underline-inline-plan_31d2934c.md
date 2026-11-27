---
name: fac-credentials-formula-underline-inline-plan
overview: 按用户最新示例修正公式规则：源码未溯源的公式直接写成 `\underline{$...$}`，删除此前的下划线说明文字、紧贴公式下方注记及其他 underline 相关规则；凭证脚本任务保持不变。
todos:
  - id: verify-targets
    content:
      - "#text": 使用 [subagent:code-explorer] 复核公式与脚本入口
    status: completed
  - id: update-formula-rules
    content:
      - "#text": 使用 [skill:skill-creator] 更新公式与 underline 规则
    status: completed
    dependencies:
      - verify-targets
  - id: normalize-formula-readmes
    content:
      - "#text": 使用 [subagent:code-explorer] 与 [skill:lsp-code-analysis] 规范公式
    status: completed
    dependencies:
      - update-formula-rules
  - id: create-credential-core
    content:
      - "#text": 新建 scripts/credentials 核心加密与 namespace 层
    status: completed
    dependencies:
      - verify-targets
  - id: create-service-scripts
    content:
      - "#text": 新增 HPC、Gitee、WSL、API Key 脚本
    status: completed
    dependencies:
      - create-credential-core
  - id: create-manage-cli
    content:
      - "#text": 实现 manage.py 统一 CLI 与脱敏输出
    status: completed
    dependencies:
      - create-service-scripts
  - id: add-launchers-docs
    content:
      - "#text": 补充启动器、README、依赖与协议入口
    status: completed
    dependencies:
      - create-manage-cli
      - normalize-formula-readmes
  - id: validate-all
    content:
      - "#text": 校验公式写法、凭证闭环、脚本与文档门禁
    status: completed
    dependencies:
      - add-launchers-docs
---

## 用户要求
- 修正 FeL 谱图中 `T index 00..06` 的物理含义：从对应计算文件中读取真实温度，并在图像图例中标注 Kelvin 温度。
- 修正速率类图像口径：当前“CE/RR/AI/CI 随能级编号”和“辐射跃迁速率随能级编号”是内部诊断图，不是文献常用的物理解释图；改为以波长为横轴，聚焦 10–18 Å 范围。
- 回答并落实透过率谱问题：当前结果只计算 Fe 发射谱；透过率谱需要额外光离截面、离子丰度、柱密度和背景连续谱。用户确认暂不计算，只在报告中说明所需数据和公式。
- 保持科研绘图风格：英文标注、Times New Roman、字号大于 18pt。
- 所有相关脚本、数据、图像、报告和说明仍集中在 `scenarios/fac_demo/cases/FeL_single_node/` 子场景目录内。

## 核心功能
- 从 HPC 的 PFAC 环境导出与 FeL 谱图文件对应的真实温度网格。
- 重绘谱图，以真实温度替换文件序号标签。
- 建立 `.rt` 速率表能级到 `.sp` 谱表绝对能量/波长的映射，重绘速率与跃迁速率图。
- 更新 `FeL仿真报告.html`，修正图注、方法说明和透过率谱限制说明。
- 完成脚本、图像引用、文档门禁和格式校验。

## 技术栈选择
- 绘图：本地 Python 3 + matplotlib，沿用当前 `plots/plot_style.py` 的科研风格配置。
- 数据读取：纯 Python 解析 FAC 文本表 `.sp`、`.rt`，避免本地依赖 PFAC。
- 真实温度导出：通过现有 `RemoteSession` 连接 HPC，在已构建 PFAC 的 Python 3.8.6 环境中调用 `get_tgrid(26, 8)`，导出 CSV 后回传。
- 远程路径：继续从凭证与作业清单解析，不硬编码用户名。
- 报告：更新自包含 HTML `FeL仿真报告.html`，图片使用相对路径。

## 实现策略
- 不重跑 FeL 主作业；只复用 Job 4974613 已回传的完整产物和 HPC 上对应构建环境。
- `.sp` 文件单个体积大且行数可达百万级，绘图解析改为流式读取与按需缓存：
  - 谱图阶段按文件边读边累加波长直方图，避免一次性构造大量字典。
  - 速率图阶段只为所需 `.sp` 文件构建一次能级到波长映射。
- `.sp` 块元数据中的 `IBLK` 是关键字段：行内 `block/level` 需转换为 `(block, IBLK + level)`，再与 `.rt` 中的 `(block, level)` 匹配。
- 无法映射或速率非正的条目跳过并计数；若跳过比例过高则报错，避免生成误导性图像。
- 速率图横轴改为 10–18 Å 波长；正文说明该图是“按谱线波长组织的速率分布”，比内部能级编号图更接近文献中的谱线能量解释方式。

## 实施注意事项
- `abund.csv` 当前来自 `get_tgrid(26, 6)`，不能作为 FeL 谱图温度；必须新导出 `get_tgrid(26, 8)`。
- `temperatures.csv` 字段建议为 `t_index,T_K,log10T`，与 `t00..t06` 文件名一一对应。
- `read_rt()` 需只读取 `NB/TR/CE/RR/AI/CI` 数据行，避免把 header 数值误判为数据。
- 图像文件可继续沿用现有文件名，减少 HTML 断链风险；必要时在文件名中体现 wavelength，但需同步更新 HTML。
- 透过率谱说明中给出 `tau(lambda) = sum_i N_i sigma_i(lambda)` 与 `T(lambda) = exp(-tau(lambda))`，强调缺少光离截面与柱密度假设，因此本轮不计算。

## 架构与目录结构
修改范围集中在 FeL 子场景：

```text
scenarios/fac_demo/cases/FeL_single_node/
├── plots/
│   ├── fac_tables.py                 # [MODIFY] 保留 IBLK 元数据；提供流式解析与能级到波长映射；修正 .rt 行识别。
│   ├── export_fel_temps.py           # [NEW] HPC 端调用 get_tgrid(26,8)，输出 temperatures.csv。
│   ├── fetch_fel_temps.py            # [NEW] 上传并运行导出脚本，回传 temperatures.csv 到子场景 artifacts。
│   ├── plot_spec.py                  # [MODIFY] 读取 temperatures.csv，图例改成真实 Kelvin 温度。
│   ├── plot_rates.py                 # [MODIFY] CE/RR/AI/CI 改为波长轴 10–18 Å。
│   ├── plot_trates.py                # [MODIFY] TR 改为波长轴 10–18 Å。
│   ├── plot_all.py                   # [MODIFY] 检查温度 CSV，统一重绘全部图像。
│   └── README.md                     # [MODIFY] 补充温度导出、波长速率图与复现命令。
├── artifacts/FeL_single_node_c24m16/plots_inputs/
│   └── temperatures.csv              # [NEW/RUNTIME] 从 HPC 导出的真实温度网格。
├── figures/
│   ├── FeL_spectrum_multitemp.png    # [UPDATE/RUNTIME] 图例使用真实温度。
│   ├── FeL_spectrum_nion.png         # [UPDATE/RUNTIME] 保持英文与科研风格。
│   ├── FeL_rates_vs_level.png        # [UPDATE/RUNTIME] 或更名后重绘为波长轴速率图。
│   ├── FeL_transition_rates.png      # [UPDATE/RUNTIME] 或更名后重绘为波长轴跃迁速率图。
│   └── 其余图像                      # [UPDATE/RUNTIME] 必要时同步重绘。
├── FeL仿真报告.html                  # [MODIFY] 修正图注、方法说明与透过率谱限制说明。
├── README.md                         # [MODIFY] 更新绘图说明与复现步骤。
└── PhySimX_fac_CHANGELOG.md          # [MODIFY] 记录物理口径修正。
```

## 验证标准
- `temperatures.csv` 包含 7 个温度点，能与 `t00..t06` 一一对应。
- 谱图图例不再出现 `T index 00` 等裸编号。
- 速率图与跃迁速率图横轴为波长 Å，范围聚焦 10–18 Å。
- HTML 中所有图片引用存在，图注与图像内容一致。
- README、公式、场景审计、MCP 自检、skill 校验和 Python 脚本语法检查全部通过。

## SubAgent
- **code-explorer**
  - Purpose: 复核 `.sp` 块元数据、`IBLK` 映射规则和 `.rt` 数据行识别方式，确认速率表到波长映射的精确字段。
  - Expected outcome: 给出可实现的映射规则、边界情况和具体文件证据，避免错误地把 header 数值当作速率数据。
