# `.circleci/` 目录说明

## 1. 目录定位

本目录包含 FAC 的 CircleCI 持续集成配置。当前只有 `config.yml`，其职责与 Travis 的编译测试矩阵不同：**CircleCI 只负责生成文档手册，并在主分支上把生成的 PDF 发布到 `release-pdf` 分支**，不负责 Python 环境、FAC 编译或 demo 测试。

配置为 CircleCI `version: 2`，工作流名为 `build-n-deploy`。文件中没有 `orbs:` 段，也没有自定义 executor。

### 触发条件

工作流通过分支过滤器区分两个任务：

| Job | 分支过滤 | 作用 |
|---|---|---|
| `build` | `ignore: master` | 在非 `master` 分支上生成文档，验证手册可被构建 |
| `deploy` | `only: master` | 仅在 `master` 分支上生成并发布 PDF |

文件没有显式配置标签触发或定时触发。

### 构建镜像与环境

`build` 和 `deploy` 都使用 Docker 镜像 `koppor/texlive`，以取得 TeX Live 文档工具链。配置中没有 `apt-get`、`conda`、pip 或其他依赖安装步骤，隐含假设该镜像已包含生成手册所需的工具。

## 2. `config.yml` 逐段说明

### 顶层结构

```yaml
version: 2
jobs:
  build:
    ...
  deploy:
    ...
workflows:
  version: 2
  build-n-deploy:
    jobs:
      - build: ...
      - deploy: ...
```

- `version: 2`：采用 CircleCI 2.0 配置格式。
- `jobs`：定义 `build` 和 `deploy` 两个独立任务。
- `workflows.version: 2`：工作流语法版本。
- `build-n-deploy`：把两个任务组合成完整流程，并通过过滤器决定各自运行的分支。

### `build` job

1. 使用 `koppor/texlive` Docker 镜像。
2. 执行名为 `Git settings` 的 `run` 步骤：
   - `git config --global user.email 'fujiisoup@gmail.com'`
   - `git config --global user.name 'fujiisoup'`
   
   这一步设置全局 Git 身份。
3. 执行 `checkout`，检出仓库源代码。
4. 执行名为 `Generating current version` 的 `run` 步骤：
   - `cd doc`
   - `make`
   
   `doc/Makefile` 的默认目标依次运行 `pdflatex manual`、`bibtex manual`、`makeindex manual` 及两次额外的 `pdflatex manual`，用于生成最新手册。`.circleci/config.yml` 随后从 `doc/manual.pdf` 复制产物，因此可确定这里生成的是 `doc/manual.pdf`。
5. `build` 到此结束，没有上传产物、测试命令或部署步骤。

### `deploy` job

1. 同样使用 `koppor/texlive` 镜像。
2. 同样先设置 Git 用户名和邮箱，再执行 `checkout`。
3. 执行 `cd doc`、`make`、`cd ../`，重新生成手册并返回仓库顶层。
4. 执行名为 `Commit to repository` 的 `run` 步骤：
   - `git checkout -b release-pdf`：创建并切换到 `release-pdf` 分支。
   - `cp doc/manual.pdf manual.pdf`：把生成的文档复制到仓库根目录。
   - `git add manual.pdf`：暂存 PDF。
   - `git commit -m "[CircleCI] Releasing PDF @$(date +'%Y/%m/%d %I:%M') [ci skip]"`：以当前日期和时间创建提交；提交信息中的 `[ci skip]` 用于避免发布提交再次触发 CI。
   - `git push -f origin release-pdf`：强制更新远程 `release-pdf` 分支，使该分支始终反映最近一次主分支文档构建结果。

`build` 和 `deploy` 是两个独立 job，配置中没有 `persist_to_workspace` 或 `attach_workspace`，因此 `deploy` 会重新 checkout 并重新生成文档，而不是复用 `build` 的 PDF。

## 3. 与其他构建和测试配置的关系

### 与 `ci/` 目录的关系

`config.yml` 中没有出现 `ci/requirements-*.yml`、`CONDA_ENV`、`conda env create` 或 Python 版本矩阵。因此：

- CircleCI 不创建 Conda 环境。
- CircleCI 不覆盖 Python 2.7、3.6、3.7 兼容性。
- CircleCI 不测试 PFAC Python 模块。
- `ci/` 中的环境文件仅由 `.travis.yml` 使用。

### 与顶层 Makefile 的关系

顶层 `Makefile.in` 由 `configure` 生成顶层 `Makefile`，其中包含：

- `all`、`lib`、`sfac`：构建数值库和 SFAC 接口。
- `pfac`、`install-pfac`：构建并安装 Python 接口。
- `doc`：执行 `cd doc; make`。
- `demo`：执行 `cd demo; make`。
- `clean`、`cleanfac`：清理构建产物。

CircleCI 没有运行 `configure`，也没有调用顶层 `Makefile` 的任何目标；它直接执行 `cd doc; make`，在效果上等同于顶层 `Makefile` 的 `doc` 目标。它不执行 `make`、`make pfac`、`make install`、`make install-pfac` 或 `make demo`。

顶层 `configure.ac` 支持 `--with-mpi=omp`，该选项会把 `USE_MPI` 设为 `2` 并加入 OpenMP 编译与链接参数。该路径由 Travis 的 `py36-openmp` 任务使用，与 CircleCI 无关。

### 与 demo 测试的关系

`demo/Makefile` 定义了 `all`、`openmp`、`check`、`clean` 和 `ref` 等目标，并在 `structure`、`excitation`、`pirr`、`aidr`、`ionization`、`polariz`、`NeL`、`tests` 子目录中依次执行对应目标。

这些 demo 测试由 `.travis.yml` 执行：

- 普通环境进入 `demo` 后执行 `make`；
- `py36-openmp` 环境执行 `make openmp`；
- 两类环境都执行 `make check`；
- 最后验证 `pfac.fac`、`pfac.crm`、`pfac.pol`、`pfac.util` 可被导入。

CircleCI 完全不调用 `demo/Makefile`，也不执行 `make check`。因此当前两套 CI 的职责是分离的：Travis 负责构建、安装、demo 验证和 Python 模块导入检查；CircleCI 负责文档构建与 PDF 发布。

## 6. README 维护记录（自底向上）

- **定位与职责**：CircleCI 只负责手册构建与 PDF 发布，不承担编译、demo 回归或 Python 环境验证。
- **底层依据**：`config.yml`、`doc/Makefile`、顶层 `Makefile.in` 的 `doc` 目标。
- **输入/输出**：输入 LaTeX 源与 TeX Live 镜像；输出 `manual.pdf` 并发布到发布分支。
- **验证与回归**：不执行 `make check`；构建成功与 PDF 产物即为该 CI 的验证标准。
- **已知限制**：与 `ci/` 的 Travis 测试职责分离，不能互相替代。
- **公式核查**：本目录无物理公式，无需下划线注记。
- **导航**：父级 [`../README.md`](../README.md)；CI 环境 [`../ci/README.md`](../ci/README.md)。

[返回上级](../README.md)
