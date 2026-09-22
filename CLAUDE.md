# TechPoster

将高质量技术博客整理成 1080×1920 手机海报，用于团队内部分享。

## 工作流程

用户提供一个文章链接 → 抓取正文 → 提炼海报文案 → 生成 HTML → Chrome headless 截图输出 PNG。

### Step 1: 抓取文章正文

使用本项目 `scripts/fetch_article.py`（已内置，仅依赖 Python 标准库），它专门处理了微信公众号的反爬 headers：

```bash
python3 scripts/fetch_article.py "<url>"

# 如需同时保留原始 HTML：
python3 scripts/fetch_article.py "<url>" --save-html /path/article.html
```

输出格式：
```
TITLE: ...
SOURCE: ...
URL: ...
---
<逐段正文，已去重>
```

### Step 2: 提炼海报内容

抓取正文后，**先判定材料类型，再按对应模块结构提炼**（类型判定与模块映射见下方「材料类型与模块分流」）。

类型 A（技术原理类）的提炼原则：
- 标题 = 一句话中心思想，压缩到一行能展示（建议 ≤20 字，保留核心词）
- 核心观点 1-2 句话，突出最有冲击力的洞见
- 技术原理 ≤200 字讲清机制，并配套生成 SVG 流程图（存于 `diagrams/diagram_<主题关键词>.svg`）
- 技术价值分析：分条列举，每条一句话，且遵循三条原则：
  - 去重：同一维度的价值只保留一条，宁可合并也不重复陈述（如成本类条目合并为一条）
  - 聚焦技术：剔除营销手段、运营数据、市场热度等非技术现象，只锚定技术特性本身
  - 单一价值点：每条只讲一个不重叠的维度（如成本 / 延迟 / 架构 / 范式），表述精准不口语化
- 适用场景写清"谁该看 / 什么时候用"
- 标签 4-5 个，覆盖技术方向 + 论文/项目名

#### 材料类型与模块分流

当前支持两类材料，新增类型时在此追加定义：

**类型 A：技术原理类（默认）**
- 特征：围绕单一技术或系统，主体是"它怎么实现的"
- 模块：核心观点 / 技术原理（机制讲解 + SVG 流程图）/ 技术价值分析 / 适用场景 / 标签
- 模板占位：`SECTION_TITLE_1` = 技术原理，`SECTION_TITLE_2` = 技术价值分析

**类型 B：行业资讯类**
- 特征：行业动态、新品发布、厂商动向、事件盘点，主体是"发生了什么"，而非机制
- 模块对应关系：
  - 核心观点：不变，提炼最有冲击力的一条判断
  - 事件全景（替代技术原理，`SECTION_TITLE_1` = 事件全景）：≤200 字梳理事件脉络、各方动作与关键数据；配套生成 SVG 全景图（时间线 / 对阵图 / 关系图，存于 `diagrams/diagram_<主题关键词>.svg`）
  - 关键信号（替代技术价值分析，`SECTION_TITLE_2` = 关键信号）：分条列举，每条一个维度；区分事实与传闻——未经官方确认的信息（灰测、代号、据传）必须标注
  - 适用场景 / 标签：不变，沿用类型 A 原则
- 禁忌：资讯类没有"技术原理"可讲，不得把厂商动态包装成机制讲解；不得为凑模块强行提炼不存在的"价值分析"

### Step 3: 生成 HTML 海报

基于 `templates/poster_template.html` 填充占位符，设计规范（尺寸、背景、字体、卡片样式）已在模板中固化，勿在 CLAUDE.md 重复维护。每篇只需：

- 选定一组主题色（蓝紫 / 蓝青 / 紫粉等）填入 `{{COLOR_*}}` / `{{*_GRADIENT}}` 占位符
- 按 6 模块填入文案，`{{SECTION_TITLE_1}}` / `{{SECTION_TITLE_2}}` 按 Step 2 判定的材料类型填入对应小节名，`{{VALUE_POINTS}}` 渲染为 `<li>` 列表项，`{{DIAGRAM_PATH}}` 指向 `../diagrams/diagram_<主题关键词>.svg`，`{{ARTICLE_URL}}` 填原始文章链接（以文本形式展示于底部，不用二维码）

### Step 4: 输出 PNG

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu \
  --screenshot=<output>.png \
  --window-size=1080,1920 --hide-scrollbars \
  file:///<path_to_html>
```

文件命名：`posters/poster_<主题关键词>.html` / `posters/poster_<主题关键词>.png`，完成后在 `POSTERS.md` 索引中追加一行。

## 项目结构

```
TechPoster/
├── CLAUDE.md                    # 本文件（工作流规范）
├── POSTERS.md                   # 已完成海报索引
├── scripts/
│   └── fetch_article.py         # 文章抓取脚本（自包含，仅标准库）
├── templates/
│   └── poster_template.html     # 海报 HTML 模板
├── raw_articles/                # 抓取的文章原始内容（txt + html）
├── diagrams/                    # 技术原理流程图（diagram_<主题关键词>.svg）
└── posters/                     # 成品海报（poster_<主题关键词>.html/png）
```

## 注意事项

- 微信公众号链接必须用 `fetch_article.py` 抓取，WebFetch 无法访问
- 如果文章很长，海报文案要敢于舍弃细节，保留结构和洞见
- Chrome headless 截图在 macOS 上会有 `CVDisplayLink` 警告，不影响输出
