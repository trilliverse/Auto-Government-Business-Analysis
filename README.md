# 面向政务部门业务清、系统清与业务流程泳道图的梳理智能体

这是一个运行在 DeepSeek Harness 中的政务业务梳理工具，主要用于：

- 从处室职责中拆分具体业务事项；
- 结合系统材料判断数字化支撑情况；
- 整理业务流程、依据和待确认问题；
- 生成 Excel 清单和 Draw.io 泳道图。

工具按阶段生成草稿，并在关键节点等待人工确认。业务人员可以修改拆分结果、调整分类、补充实际情况或退回重做，不会在未经确认的情况下直接生成最终成果。

## 使用流程

```text
确认职责材料
→ 拆分并审核业务事项
→ 分析系统支撑和业务流程
→ 审核流程依据
→ 生成并调整泳道图
```

业务人员通过 DeepSeek Harness 的浏览器页面使用，选择 **“政务流程梳理”** 智能体后，按对话提示上传材料和审核结果即可。

详细操作见：

- [业务试用指南](docs/business-pilot-guide.md)
- [职责梳理阶段说明](docs/stage1-business-guide.md)
- [GUI 会话验收说明](docs/gui-session-acceptance.md)

## 安装

需要先安装 Node.js、Python 和 DeepSeek Harness。管理员可按以下方式安装本项目：

```powershell
git clone https://github.com/trilliverse/Auto-Government-Business-Analysis.git
cd Auto-Government-Business-Analysis

python -m pip install -r requirements.txt
.\scripts\install.ps1
.\scripts\doctor.ps1
```

启动 DeepSeek Harness：

```powershell
dsh web
```

如果尚未安装 DeepSeek Harness：

```powershell
npm install -g @deepseek-ai/dsh
```

完整的部署、更新和卸载说明见 [部署指南](docs/deployment.md)。

## 项目内容

```text
distribution/gov-pipeline/   DeepSeek Harness 智能体配置
pipeline/                    业务规则、校验和导出工具
docs/                        业务与部署指南
scripts/                     安装、更新和自检脚本
```

当前包含四个 Skill：

- `governance-pipeline`：阶段编排；
- `responsibility-decomposition`：职责拆解与分类；
- `digital-support-analysis`：数字化支撑和流程分析；
- `swimlane-generation`：泳道逻辑和 Draw.io 生成。
