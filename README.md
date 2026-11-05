# JIKANG · 个人观察档案

> 把好奇心，做成现实。
>
> Paper / Pencil / Seal / Orbit — 一座持续生长的数字展馆。

这是一个为 **JIKANG** 定制的、完全可编辑的静态个人站点。使用用户提供的手绘素描与真人照片；主要呈现个人介绍、文章和 GitHub 开源作品。它既能快速发布到 GitHub Pages，也支持以后持续增加 Markdown 文章和开源项目。

**预览图**：解压后可以在 `dist/` 找到已构建好的网页。为了避免某些浏览器限制本地文件，请用下文的本地预览命令查看。

## 01｜五步发布到 GitHub Pages

### 第一步：新建仓库

在 GitHub 创建一个**公开仓库**。推荐仓库名：

- `你的GitHub用户名.github.io`（个人主页形式，网址最简洁）；或
- `jikang-site`（普通项目仓库形式）。

例如，假设 GitHub 用户名是 `yourname`：

- 仓库 `yourname.github.io` → `https://yourname.github.io/`
- 仓库 `jikang-site` → `https://yourname.github.io/jikang-site/`

**不用手动修改网站目录路径**：本项目使用相对路径，兼容以上两种 GitHub Pages 网址。GitHub Actions 还能自动推导 SEO 所需的完整站点网址。

### 第二步：把全部源码推送到仓库

解压 `jikang-personal-site.zip`，进入 `jikang-studio` 文件夹。推荐用 GitHub Desktop 提交；也可以用终端运行：

```bash
git init
git add .
git commit -m "Launch JIKANG personal archive"
git branch -M main
git remote add origin https://github.com/你的GitHub用户名/你的仓库名.git
git push -u origin main
```

请注意：需要推送**整个文件夹内部的文件**，包括隐藏目录 `.github/`，而不是只上传 `dist/`。`dist/` 是预生成网页，可用于预览；真正的自动发布会在每次提交后重新构建。

### 第三步：开启 Pages

进入该仓库的 **Settings → Pages → Build and deployment → Source → GitHub Actions**。

官方说明：[GitHub Pages 发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

### 第四步：查看部署

打开 **Actions**，找到 `Publish JIKANG Studio` 工作流。若第一次没有自动触发，可以在该工作流里选择 **Run workflow**。

部署成功后，在 **Settings → Pages** 查看到你的公开网址。首次发布、域名解析和搜索引擎收录可能需要时间。

### 第五步：换掉示例文章，开始写自己的内容

到 `content/notes/`，修改那三篇标记 `sample: true` 的示例样稿，或者直接删除后发布自己的文章。每次推送到 `main`，站点就会自动重新生成并部署。

---

## 02｜怎样修改个人信息

| 想改什么 | 编辑位置 |
| --- | --- |
| 站点名称、微信、GitHub 链接、首页主标题、站点描述 | `config.yml` |
| 个人经历、关于我的段落、名言、栏目布局 | `templates/index.html` |
| 真人照片 | `static/assets/portrait.webp` |
| 首页线描素描 | `static/assets/sketch.webp` |
| 搜索引擎 / 微信分享封面 | `static/assets/og-image.jpg` |
| 页面的色彩、排版、移动端样式 | `static/css/style.css` |
| 页面互动（菜单、复制微信、文章搜索） | `static/js/main.js` |

**重要：** 你的背景文件没有提供明确的中文姓名，因此页面使用你提出的检索称呼 `JIKANG`，没有自行编造名字。

微信 `zheng25360` 已放入配置和页面，点击按钮可复制微信号（浏览器支持安全剪贴板时）。

## 03｜如何每周发文章

这部分是整个站点后续最常用的功能。

1. 复制 `examples/新文章模板.md` 到 `content/notes/`，例如改名 `04-my-first-post.md`。
2. 修改开头的 `title / slug / date / category / description`。
3. 在 `---` 下方写 Markdown 正文，支持标题、加粗、链接、引用、列表、代码块和图片。
4. 保存并提交。GitHub Actions 会自动生成新文章的独立页面、归档入口、SEO 元数据与 RSS 订阅。

例如：

```yaml
---
title: 关于 AI 的一个真实观察
slug: a-thought-about-ai
date: 2026-11-06
category: AI 实践
description: 用一句话向读者解释，这篇文章值得读在哪里。
reading_time: 4
sample: false
draft: false
---
```

字段说明：

- `slug` 是页面网址的一部分，请只用英文小写、数字和中划线，且不可重复。
- `category` 可以任意新增，归档页分类按钮自动更新。
- `sample: true` 会在页面显示「示例样稿」，同时不进入网站地图和 RSS，且独立文章页面标为 `noindex`；正式发布改为 `false`。
- `draft: true` 是私下草稿，不会生成公开网页，改为 `false` 后才能发布。
- `date` 采用 `YYYY-MM-DD`，较新的文章优先显示。
- Markdown 里放入站点图片，可使用例如 `![配图说明](../../assets/my-image.webp)`，同时将图片保存到 `static/assets/my-image.webp`。

**直接用 GitHub 网页编辑 Markdown 也可以**，不需要每次在本地安装 Python。

## 04｜如何增加 GitHub 作品

编辑 `content/projects.yml`。第一个项目会成为首页的大型专题卡片，其余项目会自动出现在下面的作品卡片里，并各自生成详情页。

例如：

```yaml
- slug: project-two
  number: "02"
  title: A Small Idea
  subtitle: Experiment
  eyebrow: SELECTED PROJECT / 002
  category: AI 工具 · 开源探索
  summary: 一句话说清这个项目。
  description: 稍长一些的项目背景与设计初衷。
  role: 个人创作
  stack: [AI, Python, Design]
  github: https://github.com/你的用户名/你的项目
  original: https://github.com/你的用户名/你的项目
  note: 介绍限制或使用方法，避免夸大。
```

第一个项目 `TrendRadar-ORBIT` 保留了定制的「轨道星图」动态视觉。后面新增的项目自动使用更简洁的文字海报设计，也可继续扩展模板。

**项目说明的署名约定：** 当前作品使用你给出的 `nicoliustudio/TrendRadar-ORBIT` 仓库地址；该项目与开源项目 TrendRadar 有关联。设计中的 ORBIT 轨道图是概念插画，**不冒充真实软件截图**。

## 05｜本地启动预览

电脑上安装 Python 3.10+，在项目根目录运行：

```bash
python -m pip install -r requirements.txt
python build.py
python -m http.server 8000 --directory dist
```

然后打开浏览器：`http://localhost:8000`。

`dist/` 是纯 HTML / CSS / JavaScript / 图片。上线后的访客不用安装 Python、Node.js、插件或任何框架；所有文章在构建时就生成 HTML，可以单独分享网址。

## 06｜自定义域名与搜索可见性

如你有自己的域名，建议买一个短、好记、独特的域名，然后：

1. 在 `config.yml → site.url` 填写完整地址，例如 `https://example.com`。
2. 在 GitHub 仓库的 **Settings → Pages → Custom domain** 填写该域名并按 GitHub 官方要求设置 DNS；开启 HTTPS。
3. 提交新的配置触发重新构建，站点会更新 `canonical`、社交分享图片 URL、RSS 和 `sitemap.xml`。
4. 把 `https://你的域名/sitemap.xml` 提交给你需要使用的搜索引擎站长平台。

如果不使用自定义域名，则保持 `site.url` 为空。GitHub Actions 会根据仓库自动推导网址。

**短视频平台注意：** 使用「搜索 JIKANG 个人观察档案」一类统一、可检索的名称，有利于建立可辨识的个人品牌，但**不能保证搜索引擎立即收录，也不能保证不会触发平台的站外引流规则或推荐限制**。请以抖音等平台的最新规则为准。GitHub Pages 在部分网络环境下的访问情况也可能有差异，面向国内读者可以考虑后续部署到可稳定访问的国内静态托管服务，并按实际要求处理备案等事项。

## 07｜项目结构

```text
jikang-studio/
├── .github/workflows/deploy.yml  # Push 后自动发布到 GitHub Pages
├── config.yml                    # 个人站配置 / 联系方式 / SEO
├── build.py                      # 静态构建器
├── requirements.txt              # 仅用于构建
├── content/
│   ├── notes/                    # 所有文章 Markdown
│   └── projects.yml              # 作品清单
├── examples/新文章模板.md          # 写作起点（不会被公开发布）
├── templates/                   # 首页 / 列表 / 文章 / 项目 HTML 模板
├── static/
│   ├── assets/                  # 素描、照片、封面、图标
│   ├── css/style.css            # 全站视觉系统
│   └── js/main.js               # 轻量交互
├── references/个人背景与人物画像.md # 个人信息原始参考（不会部署）
└── dist/                        # 已构建的静态成品（由脚本再生成）
```

## 08｜设计与工程原则

- **视觉**：纸张材质、手绘线条、文字编辑排版、深墨绿、印章红、黄铜金，避免千篇一律的「科技渐变模板」。
- **性能**：不使用远程字体、CDN、统计脚本或 JS UI 框架；人物图片已转 WebP 格式。
- **移动端**：触控菜单、自适应版式、可读字号、无水平滚动条。
- **内容**：Markdown 作为长期维护的内容源，每篇文章有真实独立 HTML 地址。
- **可发现性**：自带标题/描述、Open Graph、结构化数据、robots.txt、RSS；在线构建时生成 sitemap.xml。
- **可访问性**：主导航语义标签、键盘焦点、图片替代文本、减少动画偏好支持。
- **安全**：访客侧不收集个人数据，不引入外部运行服务。公开个人微信是你主动提供的联系方式，可以自行删除。

---

*这是一个起点，不是定稿。愿它陪着你的作品和文章一起长大。*
