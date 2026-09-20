# 旧 DOC 与不可解析资料治理策略

## 当前现状

系统资料清单中有 13 份旧 `.doc` 和 9 份 macOS `.textClipping`。当前 Python 索引器不直接解析它们，本机也未发现 LibreOffice/antiword 可用命令。

## 原则

1. 不把不可解析文件视为已经检索；
2. 清单中保留路径、大小、SHA-256 和 `unsupported` 状态；
3. 不通过改扩展名伪装为 DOCX；
4. 不上传到不受控的在线转换网站；
5. 转换产物必须与原文件同时留存，并记录转换工具、版本、时间和新哈希；
6. 如果同一系统已有可解析 PDF/DOCX 覆盖所需内容，优先使用可解析版本，不为凑覆盖率重复转换。

## 推荐转换路径

在受控离线环境安装 LibreOffice 后，批量执行 headless 转换为 PDF 或 DOCX；转换后由业务/技术人员抽样核对页码、表格和中文文本。原 `.doc` 永不删除。

## textClipping

`.textClipping` 多为 macOS 剪贴片段，不一定是正式文档。先由人工判断其是否具有独立业务价值；如果只是同目录正式文档的残留片段，可标记为 `non-authoritative-duplicate`，不进入证据索引。

## Gate 2 要求

任何依赖旧 DOC 独有内容的结论，在成功转换并完成定位校验前只能标记为待确认，不能形成 `direct` evidence。