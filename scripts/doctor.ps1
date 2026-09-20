param([string]$DshHome)
. (Join-Path $PSScriptRoot 'preset-common.ps1')
$ctx = Get-GovPipelineContext -DshHome $DshHome
$checks = [System.Collections.Generic.List[object]]::new()
function Add-Check($Name, $Ok, $Detail) { $checks.Add([pscustomobject]@{ Check=$Name; Ok=[bool]$Ok; Detail=$Detail }) }
try { Assert-GovPipelineSource $ctx; Add-Check '发布源完整' $true $ctx.Source } catch { Add-Check '发布源完整' $false $_.Exception.Message }
$installed = Test-Path -LiteralPath $ctx.Target -PathType Container
Add-Check 'Preset 已安装' $installed $ctx.Target
if ($installed) {
    foreach ($relative in @('agent.cordis.yml','preset.yml','skills\responsibility-decomposition\SKILL.md','skills\digital-support-analysis\SKILL.md','skills\swimlane-generation\SKILL.md','skills\governance-pipeline\SKILL.md')) {
        $path = Join-Path $ctx.Target $relative
        Add-Check "存在 $relative" (Test-Path -LiteralPath $path -PathType Leaf) $path
    }
    $rootPointer = Join-Path $ctx.Target 'pipeline-root.txt'
    $rootExists = Test-Path -LiteralPath $rootPointer -PathType Leaf
    Add-Check '存在 pipeline-root.txt' $rootExists $rootPointer
    if ($rootExists) {
        $runtimeRoot = (Get-Content -LiteralPath $rootPointer -Raw -Encoding UTF8).Trim()
        Add-Check 'Pipeline 项目根目录有效' ((Test-Path -LiteralPath (Join-Path $runtimeRoot 'pipeline\src\case_status.py') -PathType Leaf) -and (Test-Path -LiteralPath (Join-Path $runtimeRoot 'pipeline\src\audit_case.py') -PathType Leaf)) $runtimeRoot
    }
    $compositionText = Get-Content -LiteralPath (Join-Path $ctx.Target 'agent.cordis.yml') -Raw -Encoding UTF8
    Add-Check 'Skills 目录已注入 composition' (-not $compositionText.Contains('__GOV_PIPELINE_SKILLS_DIR__') -and $compositionText.Contains('bundledSkillDir:')) 'bundledSkillDir'
    $sourceHash = Get-TreeDigest $ctx.Source
    $targetFiles = Get-ChildItem -LiteralPath $ctx.Target -File -Recurse | Where-Object { $_.Name -notin @('pipeline-root.txt','agent.cordis.yml') }
    $sourceFiles = Get-ChildItem -LiteralPath $ctx.Source -File -Recurse | Where-Object { $_.Name -notin @('pipeline-root.txt','agent.cordis.yml') }
    $contentMatch = ($targetFiles.Count -eq $sourceFiles.Count)
    Add-Check '安装静态内容完整' $contentMatch "sourceFiles=$($sourceFiles.Count) targetFiles=$($targetFiles.Count)"
}
$python = Get-Command python -ErrorAction SilentlyContinue
Add-Check 'Python 可用' ($null -ne $python) $(if ($python) { $python.Source } else { '未找到 python' })
if ($python) {
    $probe = & python -c "import openpyxl, pypdf; print('openpyxl='+openpyxl.__version__)" 2>&1
    Add-Check 'Python 依赖可用' ($LASTEXITCODE -eq 0) ($probe -join "`n")
}
$checks | Format-Table -AutoSize
if ($checks.Where({-not $_.Ok}).Count -gt 0) { throw 'DOCTOR FAILED：存在未通过的检查。' }
Write-Output 'DOCTOR OK。注意：Cordis 挂载有效性仍以 Harness 的 Preset mount-validation 为准。'
