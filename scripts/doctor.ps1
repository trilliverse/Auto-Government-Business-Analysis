param([string]$DshHome)
. (Join-Path $PSScriptRoot 'preset-common.ps1')
$ctx = Get-GovPipelineContext -DshHome $DshHome
Assert-GovPipelineSource $ctx
foreach ($relative in @('package.json','cordis.patch.yml','pipeline-root.txt')) {
    if (-not (Test-Path -LiteralPath (Join-Path $ctx.Source $relative) -PathType Leaf)) { throw "缺少 $relative；请运行 install.ps1。" }
}
$manifest = Get-Content (Join-Path $ctx.Source 'package.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.dsh.bundle.patch -ne './cordis.patch.yml') { throw 'bundle patch 声明无效。' }
$patch = Get-Content (Join-Path $ctx.Source 'cordis.patch.yml') -Raw -Encoding UTF8
if ($patch -match '__GOV_PIPELINE_' -or $patch -match 'dsh-workflow-worker-thread') { throw '存在未替换路径或旧插件名称。' }
$skillsPath = (Join-Path $ctx.Source 'skills').Replace('\','/')
if (-not $patch.Contains($skillsPath)) { throw 'Skills 路径与当前发布目录不符，请重新运行 install.ps1。' }
$runtimeRoot = (Get-Content (Join-Path $ctx.Source 'pipeline-root.txt') -Raw -Encoding UTF8).Trim()
foreach ($script in @('case_status.py','audit_case.py')) {
    if (-not (Test-Path -LiteralPath (Join-Path $runtimeRoot "pipeline/src/$script") -PathType Leaf)) { throw "Pipeline 根目录无效：$runtimeRoot" }
}
Write-Output "DOCTOR OK: $($manifest.name)；四个 Skills、bundle patch 和 Pipeline 根目录静态检查通过。"
Write-Output '运行时安装与发现仍须在当前客户端验证；静态检查不代表已安装。'
