# 政务流程梳理：本地 bundle 部署

## 当前格式

已按 DeepSeek Harness **0.2.0-rc.2** 核对。旧 `.agent-presets/gov-pipeline/` 目录不再是当前客户端的注册入口。项目以 `@local/gov-pipeline` 本地 bundle 安装，通过 `dsh.bundle.patch` 插入 `@deepseek-ai/dsh-agent-preset` 声明，预设 ID 保持 `gov-pipeline`，显示名称保持“政务流程梳理”。不覆盖内置预设或全局权限策略。

工作流实现使用当前 `@deepseek-ai/dsh-workflow-ptc`，不再使用已经移除的 `@deepseek-ai/dsh-workflow-worker-thread`。其余插件已对照当前 standard 预设核对。

## 准备和安装

在本仓库根目录运行：

```powershell
.\scripts\install.ps1
.\scripts\doctor.ps1
```

准备脚本生成机器相关的 `distribution/gov-pipeline/cordis.patch.yml` 和 `pipeline-root.txt`，不会复制到旧预设目录，也不会直接修改运行中的 profile。

然后在**当前客户端 → 插件管理 → 安装 bundle** 中输入 `distribution/gov-pipeline` 的完整绝对路径。例如本机：

```text
E:\scut\Research\江西交通运输数据治理\dsh\distribution\gov-pipeline
```

也可请 Agent 调用：

```json
{"action":"install_bundle","target":"E:\\scut\\Research\\江西交通运输数据治理\\dsh\\distribution\\gov-pipeline"}
```

此 bundle 没有安装脚本和外部依赖下载。当前客户端以本地 link 安装；不要删除、移动仓库。目录移动后须重新准备并安装新路径。其他机器必须先运行准备脚本，不能直接复用本机生成的绝对路径。

当前实时 profile 安装结果应为 `application: applied`。刷新预设选择界面后，新建会话选择“政务流程梳理”；已有会话可能仍保留旧预设修订。

## 路径约定

- `bundledSkillDir` 指向发布目录的 `skills` 绝对路径，包含四个 Skill。
- 预设系统提示同时提供 Python pipeline **仓库根目录**和技能目录。
- 总控 Skill 从系统提示或 bundle 根目录的 `pipeline-root.txt` 获取仓库根目录，并验证 `pipeline/src/case_status.py` 和 `audit_case.py`。
- 脚本使用仓库绝对路径；案件仍存放于业务人员指定的工作区，不存入 bundle。
- Python 可通过 `load_workspace_dependencies` 获取当前客户端自带解释器，或使用装好项目依赖的 Python。`case_status.py` 本身仅依赖标准库。

## 更新和卸载

```powershell
.\scripts\update.ps1
```

更新重新生成 patch；在客户端重新启用 bundle 以确保重载，然后新建会话。若客户端仍保留旧模块，移除并重新安装本地 bundle。卸载在当前客户端插件管理中移除 `@local/gov-pipeline`，或调用：

```json
{"action":"remove_bundle","target":"@local/gov-pipeline"}
```

旧 `.agent-presets` 目录不再参与注册，可保留作备份。更新和卸载均不删除业务案件。

## 验证与权限说明

静态检查：

```powershell
.\scripts\doctor.ps1
python -m unittest discover -s pipeline/tests -v
```

运行时需验证：预设清单中 `gov-pipeline` 无 `broken`；使用它创建新会话；该会话能发现并加载 `governance-pipeline`、`responsibility-decomposition`、`digital-support-analysis`、`swimlane-generation`；从不同于仓库的工作目录通过会话的 pwsh 工具运行绝对路径的 `case_status.py`。

本机迁移验收：上述注册、发现和加载通过。新会话默认 `workspace-write` 下出现 Windows `SetNamedSecurityInfoW failed (Win32 5): grantWrite`；同一测试会话明确选用“完全权限”后，`case_status.py` 返回退出码 0 和 Gate 0 状态。**默认沙箱权限问题未修复，bundle 不会自动提升任何业务会话的权限。** 新业务会话遇到相同错误时，应由用户选择权限或另行处理 Windows 文件权限。该运行时权限与业务人工审核不是一回事。

## 人工审核和数据边界

保留 Gate 0—3 的人工明确批准、输入版本和哈希绑定、批准产物不可覆盖、证据分层与审计链规则。“继续”、沉默、上传附件均不视为批准。测试只使用最小合成状态文件，不批准任何业务 Gate，不读写真实案件。

真实政务材料、审核记录和成果存放于受控工作区，不进入公共代码仓库。业务流程仍是：确认职责材料 → 拆解并审核事项 → 分析系统支撑与流程 → 审核泳道逻辑 → 批准后渲染交付。
