# 远程执行层

- `session.py`：唯一 SSH/SFTP 实现，密码来自加密凭证。
- `slurm_control.py`：唯一 SLURM 操作入口。
- `job_layout.py` / `job_scripts.py` / `job_submit.py`：作业目录、脚本渲染、提交。
- `fetch_policy.py` / `artifacts.py`：产物筛选与回传。
- `route_tester.py`：多线路延迟探测。

父级 [`../README.md`](../README.md)。
