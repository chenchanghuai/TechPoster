#!/usr/bin/env python3
"""海报渲染脚本：两步渲染（先测高、再按实际高度截图）。

Chrome headless 的 --screenshot 只截取 --window-size 指定的视口，不会贴合
内容高度。本脚本先渲染一份注入测高脚本的临时副本读出页面总高度，再按
实测高度截图，保证 PNG 与海报内容完全对齐、底部不被裁剪。

用法：
    python3 scripts/render_poster.py <poster.html> [output.png]

默认输出与输入同名的 .png。仅依赖 Python 标准库，需要 macOS 上已安装
Chrome。
"""
import re
import subprocess
import sys
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WIDTH = 1080

# 注入临时副本的两处修改：
# 1. 覆盖 body 的上下内边距（模板为浏览器预览保留 py-8，截图不需要边距）
# 2. 测高脚本：页面加载完成后（留 300ms 给 Tailwind CDN 生效）把 body 总
#    高度写入 <title>，--dump-dom 的输出里即可解析。
# 临时副本必须与源文件同目录生成，保证 ../diagrams/ 相对路径有效。
RENDER_OVERRIDES = """<style>body{padding-top:0!important;padding-bottom:0!important}</style>
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    var h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
    document.title = 'H:' + h;
  }, 300);
});
</script></head>"""


def chrome(args):
    return subprocess.run(
        [CHROME, "--headless", "--disable-gpu", *args],
        capture_output=True, text=True, timeout=180,
    )


def prepare_copy(html_path):
    """生成注入渲染覆盖的临时副本，返回其路径（用完需删除）。"""
    src = html_path.read_text(encoding="utf-8")
    if "</head>" not in src:
        sys.exit("渲染失败：HTML 中缺少 </head> 标签")
    tmp = html_path.with_name(html_path.stem + ".measure.html")
    tmp.write_text(src.replace("</head>", RENDER_OVERRIDES, 1), encoding="utf-8")
    return tmp


def measure_height(tmp):
    """渲染临时副本，返回页面总高度（px）。"""
    r = chrome(["--dump-dom", "--virtual-time-budget=8000",
                "--window-size=%d,1200" % WIDTH, tmp.resolve().as_uri()])
    m = re.search(r"<title>H:(\d+)</title>", r.stdout)
    if not m:
        sys.exit("测高失败：未从页面读取到高度。\n" + (r.stderr or "")[-500:])
    return int(m.group(1))


def render(tmp, out_path, height):
    r = chrome(["--screenshot=" + str(out_path),
                "--window-size=%d,%d" % (WIDTH, height),
                "--hide-scrollbars",
                tmp.resolve().as_uri()])
    if not out_path.exists():
        sys.exit("截图失败：未生成输出文件。\n" + (r.stderr or "")[-500:])


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    html_path = Path(sys.argv[1])
    if not html_path.exists():
        sys.exit("文件不存在：%s" % html_path)
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else html_path.with_suffix(".png")
    tmp = prepare_copy(html_path)
    try:
        height = measure_height(tmp)
        render(tmp, out_path, height)
    finally:
        tmp.unlink(missing_ok=True)
    print("OK %s (%dx%d)" % (out_path, WIDTH, height))


main()
