# 政务业务智能梳理工具

本项目用于辅助政府部门开展以下工作：

1. 从“三定”职责或处室职能材料中拆分业务事项；
2. 判断每项业务是否已有信息系统支撑；
3. 根据系统资料整理业务流程、依据和待确认问题；
4. 生成人工审核用 Excel；
5. 生成可继续修改的 Draw.io 泳道图。

它不是“一键生成最终结论”的工具。每个阶段都会先形成草稿，由业务人员检查、修改并明确确认后，才进入下一阶段。

---

## 一、适合哪些人使用

### 业务人员

业务人员通过浏览器中的对话页面使用，不需要编辑代码，也不需要理解 JSON、哈希或程序目录。

主要操作是：

- 提供职责和系统材料；
- 回答工具提出的范围问题；
- 审核事项拆分、数字化判断和流程；
- 明确回复“批准”或提出修改；
- 下载 Excel 和 Draw.io 成果。

### 项目管理员或技术支持人员

管理员负责一次性完成：

- 安装 DeepSeek Harness；
- 下载本项目；
- 安装“政务流程梳理”智能体；
- 配置可用的大模型；
- 为业务人员准备案件工作目录；
- 处理升级和备份。

一般业务人员不需要自行完成这些安装步骤。

---

## 二、业务人员的使用流程

安装完成后，业务人员只需要在 DeepSeek Harness 页面中操作。

### 第 1 步：选择智能体

新建会话时，选择：

```text
政务流程梳理
```

### 第 2 步：说明任务

可以直接输入：

> 新建一个处室业务梳理项目。单位是……，处室是……。我会提供职责材料。请先提取职责并让我确认，不要直接生成最终 Excel。

### 第 3 步：准备 Stage 1 材料

必须提供：

- 单位名称；
- 处室名称；
- 包含职责原文的文件；
- 职责是否来自现行正式“三定”文件；
- 本次需要全部纳入，还是排除某些职责；
- 本项目的特殊口径，没有则说明“无”。

**不需要重复上传通用的职能梳理工作指引。**相关方法已经内置在智能体中。

### 第 4 步：审核职责事项

智能体会先展示职责提取结果，然后生成事项拆解草稿。业务人员重点检查：

- 有没有遗漏事项；
- 是否拆得过细或不够细；
- “承担、参与、指导、协助”等责任边界是否保留；
- “督导、组织、负责、参与”的分类是否正确；
- 领导交办等兜底事项是否纳入。

如果需要修改，可以直接说：

> 第 5 项分类改为待确认。

> 第 8 条职责本次不纳入正式清单，但要保留审核记录。

只有明确回复类似下面的话，系统才会进入下一阶段：

> 批准当前事项清单，进入下一阶段。

“看起来还可以”“继续说”“下一步是什么”都不会被当作批准。

### 第 5 步：补充系统资料

第二阶段需要提供与事项相关的材料，例如：

- 系统需求说明书；
- 概要设计、详细设计或初步设计；
- 操作手册；
- 数据库设计；
- 业务制度；
- 实际办理样例；
- 系统名称和编号清单。

智能体会先建立资料目录和证据候选，再分析数字化情况。业务人员需要检查：

- 系统资料是否与事项的业务范围一致；
- 是否错误混用了高速公路、普通干线、农村公路或道路运输材料；
- 目标处室是否被错误写成主责或审批主体；
- 待确认问题是否完整；
- 引用的文件、页码或段落是否正确。

### 第 6 步：审核业务流程

第二阶段确认后，可以得到九列 Excel，其中包含：

- 职责和事项；
- 职能类型；
- 是否有数字化支撑；
- 流程和待确认问题；
- 关联系统；
- 流程依据。

泳道图列在这一阶段保持为空。

### 第 7 步：审核泳道图

智能体先生成泳道逻辑草稿，业务人员确认：

- 泳道中的主体是否正确；
- 节点顺序是否正确；
- 审核、退回和重新提交路径是否准确；
- 最终成果是什么；
- 信息系统是否只作为支撑说明，而不是被画成业务主体。

确认逻辑后，系统生成多页 Draw.io 文件。Draw.io 文件仍建议由业务人员或项目人员进行一次排版调整。

更完整的业务操作说明见 [`docs/business-pilot-guide.md`](docs/business-pilot-guide.md)。

---

## 三、管理员安装指南（Windows）

下面的步骤通常由项目管理员或技术支持人员执行一次。

### 1. 安装基础软件

#### Node.js

安装 Node.js 的长期支持版（LTS）。安装完成后打开 PowerShell，检查：

```powershell
node --version
npm --version
```

如果能显示版本号，说明安装成功。

#### Python

建议安装 Python 3.11 或更新的稳定版本。安装时勾选 **Add Python to PATH**。

检查：

```powershell
python --version
```

#### Git

如果管理员使用 Git 获取和更新本项目，请安装 Git：

```powershell
git --version
```

不熟悉 Git 的用户也可以在 GitHub 页面下载 ZIP，由管理员解压后安装。

### 2. 安装 DeepSeek Harness

DeepSeek Harness 当前通过 npm 发布。可以全局安装：

```powershell
npm install -g @deepseek-ai/dsh
```

启动浏览器界面：

```powershell
dsh web
```

启动后命令行会显示一条 `dsh web:` 地址，通常会自动打开浏览器。如果没有自动打开，请复制命令行显示的完整地址到浏览器。

> 本项目开发和验收时使用的是 `@deepseek-ai/dsh 0.1.5-rc.2`。npm 默认会安装当时发布的最新版；如果后续版本变化较大，建议由管理员先在测试环境验证，并按需安装兼容版本。升级前请备份业务案件目录。

如果不希望全局安装，也可以使用 npm 的临时运行方式；但面向业务人员部署时，建议由管理员统一安装和维护，避免每次下载版本不同。

### 3. 配置大模型

打开 DeepSeek Harness 后，在页面的模型或设置区域配置本单位允许使用的模型服务和凭证。

建议由管理员统一完成，并确认：

- 模型可以正常对话；
- 敏感材料允许发送到所选模型；
- API 凭证不写入项目文件或业务附件；
- 网络和数据出境要求符合本单位规定。

本项目不包含任何模型 API Key。

### 4. 下载本项目

使用 Git：

```powershell
git clone https://github.com/trilliverse/Auto-Government-Business-Analysis.git
cd Auto-Government-Business-Analysis
```

或者在 GitHub 页面选择 **Code → Download ZIP**，解压后在该目录打开 PowerShell。

### 5. 安装 Python 依赖

在项目目录运行：

```powershell
python -m pip install -r requirements.txt
```

### 6. 安装“政务流程梳理”智能体

在项目目录运行：

```powershell
.\scripts\install.ps1
.\scripts\doctor.ps1
```

如果 PowerShell 阻止本次脚本执行，可仅对当前窗口临时放行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

然后重新执行安装命令。是否允许执行脚本应遵循本单位终端安全管理要求。

`doctor.ps1` 最后显示：

```text
DOCTOR OK
```

说明智能体文件、Skills、Python 和项目路径检查通过。

### 7. 重新启动 Harness

关闭原来的 Harness 进程，然后重新运行：

```powershell
dsh web
```

新建会话时应能看到：

```text
政务流程梳理
```

### 8. 更新本项目

Git 安装方式：

```powershell
git pull
.\scripts\update.ps1
.\scripts\doctor.ps1
```

ZIP 安装方式需要管理员下载新版本、备份旧目录，再运行更新脚本。

更新智能体不会删除业务案件目录。

### 9. 卸载智能体

```powershell
.\scripts\uninstall.ps1 -KeepBackup
```

该命令只卸载智能体配置，不会删除业务材料和案件成果。

更详细的部署说明见 [`docs/deployment.md`](docs/deployment.md)。

---

## 四、如何保存业务项目

建议每个项目使用独立目录，例如：

```text
D:\政府业务梳理项目\
└─ 2026-养护技术服务处\
   ├─ 原始材料\
   ├─ 系统资料\
   └─ workcases\
```

不要把真实政务材料直接放进本代码仓库。以下目录已默认排除，不会被 Git 跟踪：

```text
example/
reference-materials/
workcases/
```

仍建议业务人员遵守本单位的文件分级、访问控制、脱敏和备份规定。

系统需求书、数据库设计和操作手册可能包含：

- 联系人和电话；
- 内部地址；
- 用户名或字段结构；
- 系统架构和权限信息。

上传模型前应确认使用范围。不要将内部资料提交到公开 GitHub，也不要使用不受控的在线文档转换服务。

---

## 五、常见问题

### 页面里找不到“政务流程梳理”

依次检查：

```powershell
.\scripts\doctor.ps1
.\scripts\update.ps1
```

然后完全重启 `dsh web`，再新建会话。

### Doctor 没有显示 OK

将完整错误信息交给管理员处理。不要手工复制文件到未知目录，也不要修改 DeepSeek Harness 自带的 Preset。

### 模型没有停在人工审核点

明确告诉模型：

> 请停在当前 Gate，只生成审核稿，不要替我批准或进入下一阶段。

并保留该会话用于问题排查。GUI 验收检查表见 [`docs/gui-session-acceptance.md`](docs/gui-session-acceptance.md)。

### 为什么有些事项是“待确认”

“待确认”通常表示：

- 当前资料没有覆盖主要流程；
- 系统功能与事项范围不完全一致；
- 目标处室权限不明确；
- 只有数据字段，没有实际办理流程证据。

资料不足不能直接判断为“无”。

### 可以直接采用生成的泳道图吗

不建议。应先核对业务主体、节点、判断、退回路径和最终成果，再调整 Draw.io 排版。

---

## 六、管理员检查和测试

日常自检：

```powershell
.\scripts\doctor.ps1
```

运行自动测试：

```powershell
python -m unittest discover -s pipeline/tests -v
```

冷启动全流程测试：

```powershell
.\scripts\test-cold-start.ps1
```

查看某个案件当前阶段：

```powershell
python pipeline/src/case_status.py workcases/<案件ID>
```

生成案件审计报告：

```powershell
python pipeline/src/audit_case.py workcases/<案件ID>
```

这些命令主要由管理员使用，业务人员通常不需要运行。

---

## 七、项目文档

- [`docs/business-pilot-guide.md`](docs/business-pilot-guide.md)：业务试用操作；
- [`docs/deployment.md`](docs/deployment.md)：部署、更新和离线交付；
- [`docs/gui-session-acceptance.md`](docs/gui-session-acceptance.md)：GUI 新会话验收；
- [`docs/stage1-business-guide.md`](docs/stage1-business-guide.md)：职责梳理阶段说明；
- [`pipeline/docs/architecture.md`](pipeline/docs/architecture.md)：技术架构；
- [`pipeline/docs/stage1-method-basis.md`](pipeline/docs/stage1-method-basis.md)：内置职责梳理方法；
- [`pipeline/docs/legacy-document-policy.md`](pipeline/docs/legacy-document-policy.md)：旧版 DOC 等资料处理原则。

## 八、许可证

本项目采用 MIT License，见 [`LICENSE`](LICENSE)。
