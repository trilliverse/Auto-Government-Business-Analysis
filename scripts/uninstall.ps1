param(
    [string]$DshHome,
    [switch]$KeepBackup
)
. (Join-Path $PSScriptRoot 'preset-common.ps1')
$ctx = Get-GovPipelineContext -DshHome $DshHome
if (-not (Test-Path -LiteralPath $ctx.Target -PathType Container)) {
    Write-Output "Preset 未安装，无需卸载：$($ctx.Target)"
    exit 0
}
if ($KeepBackup) {
    $backupRoot = Join-Path $ctx.DshHome '.agent-presets-backup'
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    $backup = Join-Path $backupRoot "gov-pipeline-uninstall-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Move-Item -LiteralPath $ctx.Target -Destination $backup
    Write-Output "Preset 已移至备份：$backup"
} else {
    Remove-Item -LiteralPath $ctx.Target -Recurse -Force
    Write-Output "Preset 已删除：$($ctx.Target)"
}
Write-Output '案件目录和工作区文件未被删除。'
