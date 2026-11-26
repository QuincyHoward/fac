# 08 打包与发布

- `package.py`：构建 sdist/wheel，可选 `twine check`。
- `publish_pypi.py`：从加密凭证读取 PyPI/TestPyPI Token，通过环境变量传给 twine。

```bash
python scripts/08_release/package.py --check
python scripts/08_release/publish_pypi.py --test -n
python scripts/08_release/publish_pypi.py
```

父级 [`../README.md`](../README.md)。
