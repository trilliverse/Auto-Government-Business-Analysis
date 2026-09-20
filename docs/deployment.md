# 政务流程梳理 Agent 交付与部署

## 交付边界

Git/内网代码仓库保存程序源代码、Preset、Skills、Schema、测试和脱敏案例。真实政务材料、审核记录和成果不进入公共仓库；它们保存在业务人员指定的受控工作区。

## 管理员安装

在项目根目录运行：

```powershell
.\scripts\doctor.ps1
.\scripts\install.ps1
```

默认安装到：

```text
${DSH_HOME:-$HOME/.dsh}/.agent-presets/gov-pipeline/
```

安装后重启或刷新 DeepSeek Harness，新建会话时选择“政务流程梳理”。不要修改 Harness 随附的 `standard`、`cordis` 等 Preset。

如果当前机器已存在同名 Preset：

```powershell
.\scripts\update.ps1
```

更新会先备份旧 Preset，不触碰案件目录。卸载：

```powershell
.\scripts\uninstall.ps1 -KeepBackup
```

## 离线和内网交付

可选方式：

1. 单位内部 GitLab/Gitea 仓库；
2. 经审核的 ZIP 发布包；
3. 内网制品库。

业务数据应与程序仓库分离。示例材料进入发布包前必须脱敏并经授权。

## 业务人员使用流程

1. 在 Harness 新建会话，选择“政务流程梳理”；
2. 指定新的案件工作目录；
3. 上传或引用目标单位的职责来源材料，并说明纳入/排除范围和特殊口径；工作指引方法已经内置，无需每个案件重复上传；
4. Agent 提取单位、处室和职责，生成 Gate 0 审核稿；
5. 业务人员确认或提出修改；
6. Agent 生成职责拆解草稿，业务人员完成 Gate 1；
7. 从批准数据导出 Excel；
8. 后续继续数字化支撑、证据流程和泳道图审核。

业务人员无需操作 JSON、哈希或 Cordis 配置；这些用于后台版本控制和审计。

## 当前成熟度

当前属于开发者/试用版：Stage 1 已完成结构化、审核、冻结和 Excel 导出；Stage 2、Stage 3 仍在开发。安装脚本复制的是仓库内 `distribution/gov-pipeline/` 标准源。

## 案件状态与审计

管理员可随时运行：

```powershell
python pipeline/src/case_status.py workcases/<case-id>
python pipeline/src/audit_case.py workcases/<case-id>
```

前者显示当前 Gate、批准产物和下一步操作；后者校验 Gate 0—3 的哈希链、上游绑定和交付物，并生成 `reviews/case-audit.json` 与 `reviews/case-audit.md`。审计报告通过不等于业务未决问题已经解决，真实交付仍须查看报告中的未决事项。

## 发布前检查

```powershell
.\scripts\doctor.ps1
python -m unittest discover -s pipeline/tests -v
```

`doctor.ps1` 检查文件、安装一致性、Python 和依赖。Cordis 的最终挂载验证需由运行中的 Harness 调用 Preset mount-validation；文件摘要一致不等同于运行时挂载成功。