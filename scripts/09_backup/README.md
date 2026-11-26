# 09 发布前备份

`backup.py` 仿 FLASH 双模式备份：

- `gitee`：按 `git ls-files` 与未跟踪未忽略文件复制。
- `full`：排除 `.git/build/dist/__pycache__/outputs/runs/logs` 后近全量复制。

```bash
python scripts/09_backup/backup.py --mode gitee --dest <DIR> -n
python scripts/09_backup/backup.py --mode full --dest <DIR>
```

父级 [`../README.md`](../README.md)。
