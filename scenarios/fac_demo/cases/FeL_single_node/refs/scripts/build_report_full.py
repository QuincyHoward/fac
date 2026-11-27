#!/usr/bin/env python3
"""Build the full-physics FAC-vs-literature comparison HTML report."""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build_report import LITERATURE_TABLE, img_tag, table_html  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--scene-dir", required=True)
    parser.add_argument("--html", required=True)
    parser.add_argument("--overlay", default="")
    parser.add_argument("--pi-figure", default="")
    args = parser.parse_args()

    scene = Path(args.scene_dir).resolve()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    sections = []
    for pair in manifest:
        side = Path(pair.get("side_by_side", ""))
        if not side.is_absolute():
            side = scene / side
        sections.append(
            '<section class="compare-card" id="%s"><h3>%s — %s</h3>%s'
            '<p class="caption"><strong>文献：</strong>%s</p>'
            '<p class="note"><strong>对照：</strong>%s</p></section>' % (
                pair["id"], pair["id"], pair.get("figure", ""),
                img_tag(side, pair["id"]), pair.get("caption", ""), pair.get("notes", ""),
            )
        )

    overlay = img_tag(Path(args.overlay), "full digitized overlay") if args.overlay and Path(args.overlay).exists() else '<p class="note">未生成叠加图。</p>'
    pi = img_tag(Path(args.pi_figure), "FAC PI cross sections") if args.pi_figure and Path(args.pi_figure).exists() else '<p class="note">未生成 PI 图。</p>'

    html = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>FAC full-physics 与文献对比图分析报告</title>
<style>
:root{--primary:#244B7A;--secondary:#2F6FA8;--bg:#fff;--soft:#F7F9FC;--text:#202020;--muted:#555;--line:#DDD;--accent:#B23A3A}
*{box-sizing:border-box}body{font-family:"Times New Roman","SimSun",serif;font-size:16px;line-height:1.68;color:var(--text);max-width:1280px;margin:0 auto;padding:28px 32px 80px;background:var(--bg)}
h1{font-size:30px;font-weight:600;color:var(--primary);border-bottom:3px solid var(--primary);padding-bottom:12px}
h2{font-size:21px;color:var(--primary);margin-top:38px;border-left:5px solid var(--secondary);padding-left:12px}
h3{font-size:18px;color:var(--secondary);margin:0 0 10px}
nav{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.95);border-bottom:1px solid var(--line);padding:10px 0;margin-bottom:22px}
nav a{color:var(--primary);text-decoration:none;margin-right:16px}nav a:hover{color:var(--accent)}
.hero{background:linear-gradient(135deg,#F7F9FC,#EEF4FA);border:1px solid var(--line);border-radius:10px;padding:18px 22px;box-shadow:0 4px 18px rgba(36,75,122,.08)}
.note{background:var(--soft);border-left:4px solid var(--secondary);padding:10px 14px;margin:12px 0;color:var(--muted)}
.caption{font-size:15px;color:var(--muted);margin:8px 0}table{border-collapse:collapse;width:100%;margin:16px 0;font-size:15px}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}th{background:#EEF3F8;color:var(--primary)}
.compare-card{border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:20px 0;box-shadow:0 3px 14px rgba(36,75,122,.06)}
.report-image{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff}
code{background:#F2F4F7;padding:2px 5px;border-radius:4px}footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:14px}
@media print{nav{position:static}body{max-width:none;padding:0}.compare-card{box-shadow:none;page-break-inside:avoid}}
</style></head><body>
<nav><a href="#summary">摘要</a><a href="#conditions">文献条件</a><a href="#comparisons">图像对照</a><a href="#overlay">叠加</a><a href="#pi">PI</a><a href="#conclusions">结论</a></nav>
<h1>FAC full-physics 与文献对比图分析报告</h1>
<section id="summary" class="hero"><p>本报告基于 <code>opacity_full/</code> full-physics 场景：打开 bound-bound 吸收、采用 Doppler/Stark/自然宽度 Voigt 线型、密集 PI 与示例级 AI/DR 共振贡献，并与文献截取图并列对照。</p>
<p class="note"><strong>边界：</strong>文献多为高密度 LTE / Z-pinch；本场景为 0D 光薄 CRM，输出 cm²/Fe ion。无机器可读基准，不做自动回归，只做图像级定性与半定量对照。</p></section>
<h2 id="conditions">1. 文献条件</h2>__TABLE__
<h2 id="comparisons">2. 文献图 / FAC full 图并列对照</h2>__SECTIONS__
<h2 id="overlay">3. 数字化叠加</h2>__OVERLAY__
<h2 id="pi">4. FAC 光电离截面</h2>__PI__
<h2 id="conclusions">5. 结论</h2><ul>
<li>full-physics 谱已包含 bound-bound 谱线结构，线宽来自 Doppler、自然宽度与可用的 Stark/impact 字段。</li>
<li>密集 PI 与 AI/DR 共振贡献改善准连续体和共振结构，但 AI/DR 为示例级近似，不是实验级 R-matrix 结果。</li>
<li>仍不能与文献绝对不透明度逐点比对：电离平衡、密度、辐射转移和面密度条件不同。</li>
<li>所有源图、裁剪框、FAC 对应图和阶段状态见 <code>refs/figures/figure_manifest_full.json</code> 与 <code>opacity_full/outputs/</code>。</li>
</ul><footer>生成脚本：<code>refs/scripts/build_report_full.py</code>　自包含 HTML，可离线查看。</footer></body></html>"""
    html = (html.replace("__TABLE__", table_html(LITERATURE_TABLE, ["文献", "条件", "等离子体状态", "能区", "用途"]))
                .replace("__SECTIONS__", "\n".join(sections))
                .replace("__OVERLAY__", overlay)
                .replace("__PI__", pi))
    out = Path(args.html).resolve()
    out.write_text(html, encoding="utf-8")
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
