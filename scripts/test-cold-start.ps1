param(
    [string]$CaseId = 'cold-start-acceptance',
    [switch]$KeepCase
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$caseDir = Join-Path $repo "workcases\$CaseId"
if (Test-Path -LiteralPath $caseDir) { Remove-Item -LiteralPath $caseDir -Recurse -Force }
$env:PYTHONIOENCODING='utf-8'
function Run-Python([string[]]$Arguments) {
    & python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Python command failed: python $($Arguments -join ' ')" }
}
try {
    Run-Python @('pipeline/src/intake.py','--workbook','example/公路域信息系统整合需求梳理表-综交中心养护处.xlsx','--case-id',$CaseId,'--output-root','workcases')
    Run-Python @('pipeline/src/confirm_stage1_input.py',$caseDir,'--source-type','working-sheet-copy','--authority-status','not-verified','--source-notes','冷启动验收：工作簿文本，未核验正式三定文件','--scope-mode','exclude-list','--exclude','R008','--scope-notes','按脱敏开发Gold排除领导交办事项','--special-rule','仅用于冷启动机械链验收','--confirmed-by','cold-start-test')
    Run-Python @('pipeline/src/review_gate.py','decide',$caseDir,'--decision','approved','--reviewer','cold-start-test','--comments','冷启动 Gate 0')
    Run-Python @('pipeline/src/review_gate.py','advance',$caseDir)
    Run-Python @('pipeline/src/build_stage1_baseline.py',$caseDir,'--reference','pipeline/fixtures/maintenance-office-stage1-reference.json')
    Run-Python @('pipeline/src/validate_stage1.py',$caseDir,'--reference','pipeline/fixtures/maintenance-office-stage1-reference.json')
    Run-Python @('pipeline/src/review_stage1.py','decide',$caseDir,'--decision','approved','--reviewer','cold-start-test','--comments','冷启动 Gate 1')
    Run-Python @('pipeline/src/review_stage1.py','freeze',$caseDir)
    Run-Python @('pipeline/src/export_stage1_excel.py',$caseDir)
    Run-Python @('pipeline/src/advance_stage2.py',$caseDir)
    Run-Python @('pipeline/src/index_documents.py',$caseDir,'--input','reference-materials/公路域15个系统/4江西省公路养护综合监管系统','--input','reference-materials/公路域15个系统/5 江西省公路交通情况调查系统','--input','reference-materials/公路域15个系统/8 江西省普通干线路网运行监测与应急处置平台（二期）','--scope-note','冷启动代表资料索引')
    Run-Python @('pipeline/src/build_stage2_baseline.py',$caseDir,'--reference','pipeline/fixtures/maintenance-office-stage2-reference.json')
    Run-Python @('pipeline/src/validate_stage2.py',$caseDir)
    Run-Python @('pipeline/src/review_stage2.py','decide',$caseDir,'--draft','stage-2/drafts/assessments-baseline-v1.json','--decision','approved','--reviewer','cold-start-test','--comments','冷启动 Gate 2：使用人工Gold基线，仅验收机械链')
    Run-Python @('pipeline/src/review_stage2.py','freeze',$caseDir)
    Run-Python @('pipeline/src/export_stage2_excel.py',$caseDir)
    Run-Python @('pipeline/src/build_stage3_baseline.py',$caseDir)
    Run-Python @('pipeline/src/validate_stage3.py',$caseDir)
    Run-Python @('pipeline/src/review_stage3.py','decide',$caseDir,'--decision','approved','--reviewer','cold-start-test','--comments','冷启动 Gate 3')
    Run-Python @('pipeline/src/review_stage3.py','freeze',$caseDir)
    Run-Python @('pipeline/src/render_drawio.py',$caseDir)
    Run-Python @('pipeline/src/audit_case.py',$caseDir)
    Write-Output "COLD START ACCEPTANCE OK: $caseDir"
} finally {
    if (-not $KeepCase -and (Test-Path -LiteralPath $caseDir)) {
        Remove-Item -LiteralPath $caseDir -Recurse -Force
        Write-Output "Cleaned: $caseDir"
    }
}
