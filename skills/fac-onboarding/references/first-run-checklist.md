# 首次运行检查清单

## 1. 构建完整性

- `libfac.a` 存在且大小非零。
- `sfac`、`scrm`、`spol` 可执行文件存在。
- 构建目录中存在四个 PFAC 扩展模块。
- `python/version.py` 与 `python/consts.py` 由构建流程生成，来源可追溯。

## 2. Python 导入

```bash
python3 -c "from pfac import fac, crm, pol, util; print('PFAC OK')"
```

通过标准：输出 `PFAC OK`，无符号未定义、无版本冲突、无路径错误。

## 3. demo 冒烟回归

选择低资源、带基准的算例执行：

```bash
cd <WORK_ROOT>/demo
make check
```

通过标准：

- 每个 `check.py` 调用返回 0。
- 屏幕输出 `Tests passed!`。
- 没有 `TypeError: Unknown file extension`。
- 输出表文件名与 `RESULTS` 列表一致。

## 4. 产物检查

| 表类型 | 头部检查 | 数值检查 |
|---|---|---|
| `.en` | `NBlocks`、`E0` | 能量单位、字符串列 |
| `.tr` | 块数 | `gf`、`rate`、跃迁能 |
| `.ce` / `.ci` | 能量网格 | 碰撞强度非负、截面单位 |
| `.rr` | 通道块 | RR/PI 正值、参数数量 |
| `.ai` | 束缚/自由索引 | AI 率、DC 强度 |
| `.sp` / `.rt` | `TYPE`、`NBlocks` | 布居归一、谱强度口径 |
| `.ham` | 二进制块 | 用读取器解析，不用文本编辑器 |

## 5. 记录模板

| 项目 | 记录内容 |
|---|---|
| 环境 | OS、编译器版本、Python 版本 |
| 构建选项 | `configure` 参数、ABI 开关、OpenMP 选项 |
| 导入 | `PYTHONPATH`、导入命令、输出 |
| 冒烟 | 运行的 check 项、退出码 |
| 耗时 | 有实测则写起止时间；否则写“未记录” |
| 异常 | 警告、失败、保留的日志路径 |

## 6. 不通过时的分流

- 导入失败：回到“导入与路径检查”，优先查路径和 ABI。
- `make check` 扩展名错误：检查文件名是否被改动。
- 数值差异：先查表头、行序、容差、死键、单位，再怀疑物理实现。
- 无基准目录：不要写“回归通过”，改为产物完整性与物理合理性检查。
