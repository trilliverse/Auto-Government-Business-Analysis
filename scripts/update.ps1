param([string]$DshHome)
# Regenerate the linked local bundle; use the current client's bundle manager
# to disable/enable @local/gov-pipeline if its watcher has not reloaded it.
& (Join-Path $PSScriptRoot 'install.ps1') -DshHome $DshHome
Write-Output '然后在客户端插件管理中重新启用 @local/gov-pipeline，新建会话使用新版本。'
