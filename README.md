# Auto Government Business Analysis

面向政府部门职责、数字化支撑和业务流程梳理的 DeepSeek Harness 半自动化 Pipeline。

核心原则：

- 结构化 JSON 是事实源，Excel、Markdown、Draw.io 是审核或交付视图；
- AI 只生成草稿，人工作出唯一阶段放行决定；
- 每个 Gate 绑定输入版本和 SHA-256；
- 上游批准版本变化会使下游成果失效；
- 直接证据、分析推导、人工补充和待确认问题严格分层；
- 真实政务材料和案件数据不进入代码仓库。

## 流程

```text
Gate 0 输入确认
  → Stage 1 职责拆解与分类
  → Gate 1 冻结事项版本、导出四列 Excel
  → Stage 2 文档索引、证据筛选、数字化与流程分析
  → Gate 2 冻结分析版本、导出九列 Excel
  → Stage 3 泳道逻辑建模
  → Gate 3 冻结逻辑、渲染多页 Draw.io
```

## 主要目录

```text
distribution/gov-pipeline/   可发布的 Agent Preset 与 Skills
pipeline/src/                确定性提取、校验、冻结和导出工具
pipeline/schemas/            阶段数据 Schema
pipeline/skills/             业务方法 Skills 源文件
pipeline/docs/               架构、方法和验收记录
docs/                        安装、业务试用和 GUI 验收说明
scripts/                     安装、更新、自检、卸载和冷启动测试
```

## 安装

要求：Windows PowerShell、Python，以及 DeepSeek Harness。Python 依赖：

```powershell
python -m pip install openpyxl pypdf
```

安装专用 Preset：

```powershell
.\scripts\install.ps1
.\scripts\doctor.ps1
```

更新：

```powershell
.\scripts\update.ps1
```

然后在 DeepSeek Harness 新建会话时选择 **政务流程梳理**。

## Skills

- `governance-pipeline`：案件新建、恢复和 Gate 编排；
- `responsibility-decomposition`：职责原子化和职能类型标注；
- `digital-support-analysis`：数字化判断、流程、系统和证据分层；
- `swimlane-generation`：先审逻辑再渲染 Draw.io。

## 验证

```powershell
python -m unittest discover -s pipeline/tests -v
.\scripts\doctor.ps1
.\scripts\test-cold-start.ps1
```

真实 GUI 验收见 `docs/gui-session-acceptance.md`。

## 数据与安全边界

仓库不会跟踪：

- `example/` 中的实际附件；
- `reference-materials/` 系统设计资料；
- `workcases/` 案件数据、审核记录与交付成果；
- ZIP 包和本机运行时路径。

请将业务材料保存在受控目录。不要提交联系人、电话、系统凭证、内部设计文档或未脱敏成果。旧 `.doc` 不上传在线转换网站，处理策略见 `pipeline/docs/legacy-document-policy.md`。

## 文档

- `docs/deployment.md`：部署和离线交付；
- `docs/business-pilot-guide.md`：业务试用；
- `docs/gui-session-acceptance.md`：真实 GUI 会话验收；
- `pipeline/docs/architecture.md`：总体架构；
- `pipeline/docs/stage1-method-basis.md`：Stage 1 内置方法依据；
- `pipeline/docs/current-status.md`：开发状态和限制。

## 许可证

MIT，见 `LICENSE`。
