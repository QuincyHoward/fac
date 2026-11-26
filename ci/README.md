# `ci/` 目录说明

## 1. 目录定位

本目录存放 FAC 的 **Conda 测试环境定义文件**。4 个文件都是 Conda environment YAML，而不是 GitHub Actions、Travis 或 CircleCI 的工作流配置；它们共同描述名为 `test_env` 的环境，并统一从 `conda-forge` 渠道安装依赖。

这些文件用于覆盖 FAC 的 Python 2.7、Python 3.6 和 Python 3.7 兼容性，其中一个 Python 3.6 环境对应 OpenMP 构建分支。每个环境声明的依赖都只有：

- `python`：指定解释器版本，用于构建和加载 PFAC Python 扩展模块。
- `numpy`：提供 Python 数值数组运行时依赖；文件未给出版本约束。

所有文件均未声明 `pip` 依赖、编译器包或额外的数值库。OpenMP 并不是通过 Conda 包启用的，而是由构建阶段向 `configure` 传入 `--with-mpi=omp` 来启用。

## 2. 逐文件说明

### `requirements-py27.yml`

- 环境名：`test_env`。
- 渠道：`conda-forge`。
- 依赖：`python=2.7`、`numpy`。
- 适用场景：验证 FAC 与旧版 Python 2.7 的兼容性。
- 特殊处理：Travis 创建环境后会额外执行 `conda update -q python`，以绕过 `ContinuumIO/anaconda-issues#8437` 中提到的 Python 2.7 问题。
- OpenMP：不启用；Travis 对该环境使用普通 `./configure --prefix=$pwd$` 和 `make`。

### `requirements-py36.yml`

- 环境名：`test_env`。
- 渠道：`conda-forge`。
- 依赖：`python=3.6`、`numpy`。
- 适用场景：Python 3.6 的常规、非 OpenMP 构建与测试。
- OpenMP：不启用；Travis 使用普通 `./configure --prefix=$pwd$`，demo 阶段执行 `make`。

### `requirements-py36-openmp.yml`

- 环境名：`test_env`。
- 渠道：`conda-forge`。
- 依赖：`python=3.6`、`numpy`。
- 适用场景：Python 3.6 下的 OpenMP 并行构建与测试。
- OpenMP：**启用**。但该文件内容与 `requirements-py36.yml` 完全相同；差异由文件名对应的 `CONDA_ENV=py36-openmp` 和 Travis 中的条件命令产生：
  - 构建：`./configure --prefix=$pwd$ --with-mpi=omp`；
  - demo：`make openmp`。
- 配置依据：顶层 `configure.ac` 将 `--with-mpi=omp` 识别为 `USE_MPI=2`，默认加入 `-fopenmp -pthread`，并给 Fortran 编译加入 OpenMP 标志。

### `requirements-py37.yml`

- 环境名：`test_env`。
- 渠道：`conda-forge`。
- 依赖：`python=3.7`、`numpy`。
- 适用场景：验证 FAC 与 Python 3.7 的兼容性。
- OpenMP：不启用；使用普通配置、普通 `make` 和普通 demo 构建。

### 差异对比

| 文件 | Python 版本 | OpenMP | 依赖包 | 与其他文件的差异 |
|---|---:|---|---|---|
| `requirements-py27.yml` | `2.7` | 否 | `python=2.7`、`numpy` | 唯一的 Python 2 环境；Travis 额外升级 Python |
| `requirements-py36.yml` | `3.6` | 否 | `python=3.6`、`numpy` | 常规 Python 3.6 环境 |
| `requirements-py36-openmp.yml` | `3.6` | 是，由构建参数启用 | `python=3.6`、`numpy` | 文件内容与 `requirements-py36.yml` 相同；OpenMP 由 CI 分支逻辑决定 |
| `requirements-py37.yml` | `3.7` | 否 | `python=3.7`、`numpy` | 仅 Python 版本不同 |

## 3. 与 CI 工作流和构建脚本的关系

`.travis.yml` 直接引用了本目录。其构建矩阵为：

| `CONDA_ENV` | Python | 使用的环境文件 |
|---|---:|---|
| `py37` | `3.7` | `ci/requirements-py37.yml` |
| `py36` | `3.6` | `ci/requirements-py36.yml` |
| `py36-openmp` | `3.6` | `ci/requirements-py36-openmp.yml` |
| `py27` | `2.7` | `ci/requirements-py27.yml` |

Travis 的关键流程如下：

1. 安装 `build-essential` 和 `gfortran`。
2. 安装 Miniconda，并配置 `conda` 自动确认。
3. 执行 `conda env create --file ci/requirements-$CONDA_ENV.yml`。
4. 执行 `source activate test_env`。
5. 在 Python 2.7 环境下升级 Python；在 `py36-openmp` 环境下传入 `--with-mpi=omp`。
6. 执行 `make clean`、`make`、`make install`、`make pfac` 和 `make install-pfac`。
7. 进入 `demo`，按环境执行 `make openmp` 或 `make`，随后执行 `make check`。
8. 返回顶层，用 `python -OO` 依次导入 `pfac.fac`、`pfac.crm`、`pfac.pol` 和 `pfac.util`，确认 C 扩展模块可加载。

`.circleci/config.yml` **未引用**本目录或这些环境文件；它只构建和发布文档。仓库中的 `install.sh` 是由 X11R5 派生的通用文件安装辅助脚本，也**未引用**本目录。除 `.travis.yml` 外，未见其他 CI 配置直接使用这些 YAML。

## 4. 使用方式

这些文件是标准 Conda environment 文件，可在仓库顶层手动创建环境：

```bash
conda env create -f ci/requirements-py27.yml
conda env create -f ci/requirements-py36.yml
conda env create -f ci/requirements-py36-openmp.yml
conda env create -f ci/requirements-py37.yml
```

激活环境：

```bash
source activate test_env
```

较新的 Conda 也可以使用：

```bash
conda activate test_env
```

由于 4 个文件都把环境命名为 `test_env`，通常一次只创建其中一个。若需同时保留多个环境，可先复制 YAML 并修改 `name` 字段。手动复现 OpenMP 构建时，除创建 `requirements-py36-openmp.yml` 外，还必须执行：

```bash
./configure --prefix=$pwd$ --with-mpi=omp
make clean
make
make pfac
```

`requirements-py36-openmp.yml` 本身不会自动开启 OpenMP；必须配合上述配置参数。

## 5. README 维护记录（自底向上）

- **定位与职责**：CI 环境配置目录，记录 Python 2.7/3.6/3.7 与 OpenMP 测试环境。
- **底层依据**：`requirements-py*.yml` 与 `.travis.yml` 中的环境变量和构建命令。
- **输入/输出**：输入 Conda 环境需求；输出可用于自动化验证的 Python 环境。
- **验证与回归**：由 Travis 执行 `make`、`make check` 与 `pfac` 导入检查。
- **已知限制**：环境文件不会自动开启 OpenMP，必须配合 configure 参数。
- **公式核查**：本目录无物理公式，无需下划线注记。
- **导航**：父级 [`../README.md`](../README.md)；文档 CI [`.circleci/README.md`](../.circleci/README.md)。

[返回上级](../README.md)
