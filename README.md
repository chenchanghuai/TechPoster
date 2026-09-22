# TechPoster

将高质量技术博客整理成 **1080×1920 手机海报**，用于团队内部分享。

给一篇技术博客链接，自动走完「抓取正文 → 判定材料类型 → 提炼海报文案 → 生成 HTML → 截图输出 PNG」全流程，产出一张适合手机阅读、可直接转发的朋友圈风格海报。

## 效果示例

已完成海报见 `POSTERS.md` 索引（部分示例）：

| 主题 | 类型 |
|---|---|
| Jev 模型 22 个爆火玩法盘点与接入方式 | 行业资讯类 |
| 全球基模决战周：8 款旗舰模型挤进同一假期窗口 | 行业资讯类 |
| Jev 非生成式判断模型：三层 Agent 架构 | 技术原理类 |
| RLVR 训练熵坍缩与 STEER (ACL 2026 Outstanding Paper) | 技术原理类 |

## 工作流程

```
博客链接 → 抓取正文 → 判定材料类型 → 提炼海报文案 → 填充 HTML 模板 → Chrome 截图 → PNG
```

1. **抓取正文**：`scripts/fetch_article.py` 抓取并提取干净、去重的正文（内置微信公众号反爬 headers）
2. **判定材料类型**：对照 `CLAUDE.md` 中的「材料类型与模块分流」判定归属
   - **类型 A · 技术原理类**（默认）：主体是"它怎么实现的" → `templates/poster_principle.html`，需配套 SVG 流程图
   - **类型 B · 行业资讯类**：主体是"发生了什么" → `templates/poster_news.html`，需配套 SVG 全景图
3. **提炼文案**：按类型对应的模块结构压缩原文（核心观点 / 事件全景 / 关键信号 / 适用场景 / 标签），原则与禁忌详见 `CLAUDE.md`
4. **生成 HTML**：填充模板占位符，选定主题色，`{{DIAGRAM_PATH}}` 指向 `diagrams/` 下的 SVG 图
5. **输出 PNG**：`scripts/render_poster.py` 先测高再按实际高度截图，PNG 与内容完全对齐、底部不裁剪

详细规范（设计规范、提炼原则、模板维护纪律）见 [CLAUDE.md](CLAUDE.md)。

## 快速开始

环境要求：**Python 3**（仅标准库）+ **macOS 已安装 Chrome**（headless 截图用）。

```bash
# 1. 抓取文章正文
python3 scripts/fetch_article.py "<url>"
python3 scripts/fetch_article.py "<url>" --save-html raw_articles/article_xxx.html

# 2. 按 CLAUDE.md 工作流判定类型、提炼文案、生成 posters/poster_<关键词>.html

# 3. 渲染 PNG（默认输出同名 .png）
python3 scripts/render_poster.py posters/poster_<关键词>.html
```

完成后在 `POSTERS.md` 索引中追加一行。

## 项目结构

```
TechPoster/
├── CLAUDE.md                    # 工作流规范（类型分流、提炼原则、模板纪律）
├── README.md                    # 本文件
├── POSTERS.md                   # 已完成海报索引（本地文件，不入库）
├── TODO.md                      # 待优化项清单
├── scripts/
│   ├── fetch_article.py         # 文章抓取 + 正文提取（自包含，仅标准库）
│   └── render_poster.py         # 海报渲染：测高 + 定高截图（仅标准库）
├── templates/
│   ├── poster_principle.html    # 类型 A 模板：技术原理类
│   └── poster_news.html         # 类型 B 模板：行业资讯类
├── raw_articles/                # 抓取的文章原始内容（本地，不入库）
├── diagrams/                    # SVG 流程图 / 全景图（本地，不入库）
└── posters/                     # 成品海报 html/png（本地，不入库）
```

> 生成产物（`posters/`、`diagrams/`、`raw_articles/`）与 `POSTERS.md` 均为本地文件、不入库，仓库只跟踪工作流规范、模板与脚本。

## 注意事项

- 微信公众号链接必须用 `fetch_article.py` 抓取，常规 HTTP 工具无法访问
- Chrome headless 截图在 macOS 上会有 `CVDisplayLink` 警告，不影响输出
- 海报宽度固定 1080，高度 ≥1920 随内容自适应；渲染后仍建议目视核验整体排版与底部文章来源区
