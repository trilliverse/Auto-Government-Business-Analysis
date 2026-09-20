param([string]$DshHome)
. (Join-Path $PSScriptRoot 'preset-common.ps1')
$ctx = Get-GovPipelineContext -DshHome $DshHome
Assert-GovPipelineSource $ctx
if (-not (Test-Path -LiteralPath $ctx.Target -PathType Container)) { throw "Preset 尚未安装：$($ctx.Target)。请先运行 install.ps1。" }
$backupRoot = Join-Path $ctx.DshHome '.agent-presets-backup'
New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
$backup = Join-Path $backupRoot "gov-pipeline-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -LiteralPath $ctx.Target -Destination $backup -Recurse
$staging = "$($ctx.Target).staging"
if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
Copy-Item -LiteralPath $ctx.Source -Destination $staging -Recurse
if ((Get-TreeDigest $ctx.Source) -ne (Get-TreeDigest $staging)) { throw '暂存文件校验失败，未替换当前 Preset。' }
Remove-Item -LiteralPath $ctx.Target -Recurse -Force
Move-Item -LiteralPath $staging -Destination $ctx.Target
$compositionPath = Join-Path $ctx.Target 'agent.cordis.yml'
$skillsPath = (Join-Path $ctx.Target 'skills').Replace('\','/')
$composition = Get-Content -LiteralPath $compositionPath -Raw -Encoding UTF8
$composition = $composition.Replace('__GOV_PIPELINE_SKILLS_DIR__', $skillsPath)
Set-Content -LiteralPath $compositionPath -Value $composition -Encoding UTF8
Set-Content -LiteralPath (Join-Path $ctx.Target 'pipeline-root.txt') -Value $ctx.RepoRoot -Encoding UTF8
Write-Output "更新成功：$($ctx.Target)"
Write-Output "备份目录：$backup"
Write-Output '此操作不修改任何案件目录。请新建会话以使用更新后的 Preset。'
