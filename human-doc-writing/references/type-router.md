# 文章类型路由

先按读者要完成什么分类，再看平台和文件名。平台是载体，统领目标决定结构。

## 路由优先级

1. 用户明确指定的交付物和平台。
2. 目标文件名或路径。
3. 统领目标和阅读场景。
4. 内容素材和事实来源。
5. 语气偏好。

## 类型表

| type_id | 常见请求或路径 | 子类型示例 | 统领目标 | 类型写作卡 |
|---|---|---|---|---|
| `explainer` | 说明某概念、机制、政策、方法 | 概念解释、机制说明、方案说明 | 让读者理解一件事及其边界 | `types/explainer.md` |
| `product-doc` | 产品介绍、白皮书、产品概览 | 产品概览、设计说明、白皮书 | 帮读者理解、评估或采用产品 | `types/product-doc.md` |
| `how-to` | 快速开始、操作指南、帮助中心 | 快速开始、任务教程、故障排查 | 帮读者完成可验证的操作 | `types/how-to.md` |
| `prd` | PRD、需求说明、方案评审 | 新功能、改版、平台方案 | 帮团队形成可执行决策 | `types/prd.md` |
| `github-readme` | `README.md`、开源项目首页 | CLI、库、应用、插件 | 让访客判断项目并跑起来 | `types/github-readme.md` |
| `github-release` | Release、CHANGELOG、版本公告 | 大版本、小版本、补丁 | 让用户理解版本影响和下一步 | `types/github-release.md` |
| `wechat-article` | 公众号文章、长图文 | 观点、案例、教程、复盘 | 让读者沿一条主线形成判断 | `types/wechat-article.md` |
| `xiaohongshu` | 小红书笔记、经验/教程帖 | 经验、清单、教程、测评 | 让读者快速获得可用结论 | `types/xiaohongshu.md` |
| `social-article` | 知乎回答、论坛长帖、博客、微博/即刻等社媒中长文 | 回答、观点、经历、行业解读 | 让读者跟随材料与推理形成判断 | `types/social-article.md` |

主类型用于选择画像。它不限制文章只能有一个内容模块，也不阻止长文覆盖多个相互关联的方面。

## 关键区分

### 说明文 vs 产品文档

- 重点解释概念或机制：`explainer`。
- 重点解释产品解决什么、如何工作、是否适合：`product-doc`。

### 产品文档 vs 教程

- 帮读者理解和判断：`product-doc`。
- 帮读者完成具体操作：`how-to`。

### GitHub README vs 普通产品介绍

- 仓库首页，读者需要安装、运行、查看兼容性：`github-readme`。
- 面向产品用户，重点是问题、流程和边界：`product-doc`。

### 公众号 vs 小红书

- 需要连续论证、案例展开和完整阅读：`wechat-article`。
- 需要快速扫描、经验压缩和即时可用结论：`xiaohongshu`。

### 公众号 vs 其他社媒中长文

- 明确发布在微信公众号、需要长图文连续阅读：`wechat-article`。
- 知乎、论坛、博客、微博长文、即刻长帖或未指定平台的社媒中长文：`social-article`。
- 文章需要连续论证时，不因为平台叫“社媒”就压成短笔记。

## 文件名提示

- `README.md`：优先 `github-readme`。
- `CHANGELOG.md`、`releases/`：优先 `github-release`。
- `getting-started`、`quickstart`、`how-to`、`troubleshooting`：优先 `how-to`。
- `PRD`、`requirements`、`spec`：优先 `prd`，纯技术规范除外。
- `overview`、`whitepaper`、`product`：优先 `product-doc`。

## 多类型内容

- 一篇内容可以有一个主类型和若干内容模块。
- 平台风格只作为表达约束，不自动改变主类型。
- 如果用户同时要 README、教程和公众号稿，这是多交付物，不是一个“混合类型文件”。分别产出，再由主 Agent 统一事实和术语。

## 模糊请求处理

用户只说“写个 GitHub 文”“写个宣传文”时，先根据路径和材料预判，再在确认卡中只问一个结构性问题。不要把分类工作整包退给用户。

## 画像映射

识别到 `type_id` 后读取：

```text
user/portraits/<type_id>.md
user/anti-patterns/<type_id>.md
```

没有正向画像时，才读取：

```text
references/types/<type_id>.md
```

对用户始终显示中文名称。
