# 政务职责与数字化流程梳理 Pipeline

本目录实现 `example/instruction.md` 所描述流程的可审核、可恢复版本。设计原则是：

> 结构化数据是事实源；AI 只生成草稿；确定性工具负责读写和校验；人工作出唯一的阶段放行决定。

## 当前实现范围

当前为阶段 0 / 阶段 1 MVP：

1. 从指定 Excel 单元格提取单位、处室和职责原文；工作指引方法已内置，不是每个案件的必需附件；
2. 按中文条款编号切分职责，保留原文和来源定位；
3. 生成带 SHA-256 指纹的案件清单和 Gate 0 人工审核稿；
4. 校验案件结构、版本、来源追溯和审核状态；
5. 只有 Gate 0 获得明确批准后，才允许进入 AI 职责拆解。

本版本**不会**直接调用模型拆解职责，也不会自动进入第二阶段。

## 目录约定

```text
pipeline/
├─ docs/architecture.md
├─ schemas/case.schema.json
├─ skills/responsibility-decomposition/SKILL.md
├─ src/intake.py
├─ src/validate_case.py
└─ tests/test_intake.py

workcases/<case-id>/
├─ case.json
├─ inputs/responsibilities.json
├─ reviews/gate-0-input-review.md
├─ reviews/gate-0-decision.json       # 人工审核后创建
├─ stage-1/drafts/                    # 后续 AI 草稿
└─ stage-1/approved/                  # 后续冻结版本
```

## 运行阶段 0 输入提取

```powershell
python pipeline/src/intake.py `
  --workbook "example/公路域信息系统整合需求梳理表-综交中心养护处.xlsx" `
  --case-id "maintenance-office-demo" `
  --output-root "workcases"
```

默认从 `基本信息!B1` 读取单位、`基本信息!D1` 读取处室、`基本信息!A4` 读取职责。可通过命令行参数覆盖。

Stage 1 的必需案件输入是单位/处室、职责原文及来源、纳入排除范围和特殊口径。`example/广东省交通运输厅职能清梳理工作指引.pdf` 只用于产品方法治理，其可复用内容已提取到 `docs/stage1-method-basis.md` 和 Skill；业务人员无需重复上传。若职责存在正式调整文件或来源冲突，再将相应法规、三定文件或调整依据作为条件输入。

## 校验

```powershell
python pipeline/src/validate_case.py workcases/maintenance-office-demo
python -m unittest discover -s pipeline/tests -v
```

## Gate 0 放行语义

人工检查 `reviews/gate-0-input-review.md` 后，先确认职责来源权威性、范围和特殊口径；该步骤不需要工作指引 PDF：

```powershell
python pipeline/src/confirm_stage1_input.py workcases/maintenance-office-demo `
  --source-type working-sheet-copy `
  --authority-status not-verified `
  --source-notes "工作簿收录文本，尚未核验正式三定文件" `
  --scope-mode exclude-list --exclude R008 `
  --scope-notes "正式清单排除领导交办事项" `
  --confirmed-by "审核人"
```

然后记录 Gate 0 决定并显式推进：

```powershell
python pipeline/src/review_gate.py decide workcases/maintenance-office-demo `
  --decision approved --reviewer "审核人" --comments "职责原文及边界无误"

python pipeline/src/review_gate.py advance workcases/maintenance-office-demo
```

`advance` 会重新检查来源文件哈希、输入版本和批准决定；缺少批准、决定非批准或输入变化时都会拒绝推进。决定文件格式如下：

```json
{
  "gate": "gate-0",
  "decision": "approved",
  "reviewed_input_version": 1,
  "reviewed_responsibilities_sha256": "从 responsibilities.json 的 source.sha256 复制",
  "reviewer": "审核人",
  "reviewed_at": "2026-01-01T00:00:00+08:00",
  "comments": "职责原文和切分边界无误"
}
```

输入文件发生变化后重新运行 intake，会产生新的哈希；旧批准不得用于新输入。