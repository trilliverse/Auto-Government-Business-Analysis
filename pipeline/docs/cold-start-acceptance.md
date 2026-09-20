# 冷启动端到端验收

## 目的

验证在全新案件目录、没有当前开发会话状态的条件下，确定性工具能从 Stage 0 运行到 Gate 3，并形成可审计批准链和交付物。

## 命令

```powershell
.\scripts\test-cold-start.ps1 -KeepCase
```

## 结果

- 案件：`workcases/cold-start-acceptance/`
- Gate 0：通过；职责 8 条；输入声明确认；
- Gate 1：通过；21 条草稿、20 条纳入、1 条排除；
- Stage 1 Excel：生成成功；
- 文档索引：34 份文档、40,208 个文本块、0 失败；
- Gate 2：通过开发 Gold 基线；20 条事项，12 有、4 无、4 待确认；
- Stage 2 九列 Excel：生成成功，G 列为空；
- Gate 3：12 个泳道逻辑页面，校验通过；
- Draw.io：12 页；
- 全链审计：17 项检查全部通过，3 个交付物，15 个事项保留未决问题。

终态：

```text
gate-3 / approved
```

## 边界

这次验收验证的是机械链、版本链、Gate 和导出，不是独立模型质量。Stage 1/2 使用了开发 Gold 适配器。真实业务试用仍需通过 Preset 对话运行 Skills、人工审核并处理证据和未决问题。

## 清理

验收保留案例用于检查。需要清理时删除：

```text
workcases/cold-start-acceptance/
```

或不带 `-KeepCase` 再运行脚本，脚本结束会自动删除测试案件。