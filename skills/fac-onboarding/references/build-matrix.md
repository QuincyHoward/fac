# 构建环境矩阵与命令骨架

本文件提供首次构建与重建时可复用的命令骨架。所有外部工作目录均写作 `<WORK_ROOT>`；执行前由用户替换为真实可写路径。

## 1. 环境前提

| 项目 | 要求 | 常见失败 |
|---|---|---|
| OS/Shell | Linux 或 WSL；Windows 原生 shell 通常缺少 Fortran 工具链 | `.so` 与 Windows Python 不兼容 |
| 编译器 | `gcc` + `gfortran`，版本组合需能混编 | Fortran 符号未定义、LOGICAL 传参异常 |
| make | GNU make | shell 脚本行尾错误 |
| Python | 与编译扩展时使用的 Python 一致 | `ModuleNotFoundError`、`ImportError` |
| 工作目录 | 独立可写目录 `<WORK_ROOT>`；原始源码树只读 | 生成文件污染源码树 |

## 2. 串行前置步骤

```bash
cd <WORK_ROOT>
# 1) 归一化 shell 脚本行尾，修复 /bin/sh^M 类错误
for f in configure config.guess config.sub install.sh mkinsdir.sh; do
  sed -i 's/\r$//' "$f"
done

# 2) 配置
./configure

# 3) ABI 适配：仅在符号或调用约定失败时启用
#    只修 C/Fortran 名字修饰与 LOGICAL 约定，不触碰物理
sed -i 's/^#undef f2cFortran$/#define f2cFortran 1/' sysdef.h

# 4) 检查生成结果
ls Makefile */Makefile sysdef.h
```

`configure` 常见选项：

- `--prefix=<path>`：安装前缀。
- `PYTHON=python3` / `PYPREFIX` / `PIPOPTS`：Python 与包路径设置。
- `--with-cfortran=...`：指定 C/Fortran 桥接约定。
- `--with-mpi=omp`：启用 OpenMP 风格 MPI 初始化。
- `--enable-cpic` / `--enable-fpic`：位置无关代码选项。

以 `configure --help` 和 `configure.ac` 为准，不要凭记忆传参。

## 3. 构建产物

| 目标 | 命令骨架 | 产物 |
|---|---|---|
| C 核心库与 SFAC | `make` | `libfac.a`、`sfac/`、`scrm/`、`spol/` |
| PFAC 扩展 | `make pfac && make install-pfac` 或 `python3 setup.py build` | `pfac.fac/crm/pol/util` |
| Python 包数据 | `setup.py` 自动生成 | `python/version.py`、`python/consts.py` |

`setup.py` 会从 `faclib/consts.h` 生成 Python 常量文件；不要在未确认来源时手工编辑生成文件。

## 4. 导入检查

```bash
export PYTHONPATH=<WORK_ROOT>/build/lib.linux-*:<WORK_ROOT>/python
python3 -c "from pfac import fac, crm, pol, util; print('PFAC OK')"
```

若构建目录名因 Python 版本不同而变化，用 `ls <WORK_ROOT>/build` 确认实际路径，不要硬编码 `lib.linux-x86_64-3.10`。

## 5. 回归入口

```bash
cd <WORK_ROOT>/demo
make check
```

单项比对：

```bash
python ../check.py <RESULT> ref/<RESULT>
```

未记录耗时时写“未记录”，不要从退出码推断运行速度。
