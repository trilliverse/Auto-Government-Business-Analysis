param(
    [string]$DshHome,
    [switch]$Force
)
. (Join-Path $PSScriptRoot 'preset-common.ps1')
$ctx = Get-GovPipelineContext -DshHome $DshHome
Assert-GovPipelineSource $ctx
if (Test-Path -LiteralPath $ctx.Target) {
    if (-not $Force) { throw "Preset 已存在：$($ctx.Target)。首次安装请确认目录为空；升级请运行 update.ps1。" }
    $backup = "$($ctx.Target).backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $ctx.Target -Destination $backup
    Write-Output "已备份原目录：$backup"
}
New-Item -ItemType Directory -Force -Path $ctx.PresetRoot | Out-Null
Copy-Item -LiteralPath $ctx.Source -Destination $ctx.Target -Recurse
$sourceHash = Get-TreeDigest $ctx.Source
$targetHash = Get-TreeDigest $ctx.Target
if ($sourceHash -ne $targetHash) { throw '安装后文件校验失败。' }
$compositionPath = Join-Path $ctx.Target 'agent.cordis.yml'
$skillsPath = (Join-Path $ctx.Target 'skills').Replace('\','/')
$composition = Get-Content -LiteralPath $compositionPath -Raw -Encoding UTF8
$composition = $composition.Replace('__GOV_PIPELINE_SKILLS_DIR__', $skillsPath)
Set-Content -LiteralPath $compositionPath -Value $composition -Encoding UTF8
Set-Content -LiteralPath (Join-Path $ctx.Target 'pipeline-root.txt') -Value $ctx.RepoRoot -Encoding UTF8
Write-Output "安装成功：$($ctx.Target)"
Write-Output "内容摘要：$targetHash"
Write-Output '请重启或刷新 DeepSeek Harness，然后新建会话并选择“政务流程梳理”。'
