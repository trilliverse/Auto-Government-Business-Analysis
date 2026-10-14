param([string]$DshHome, [switch]$KeepBackup)
$ErrorActionPreference = 'Stop'
Write-Output '请在当前客户端的插件管理中移除 @local/gov-pipeline。'
Write-Output '或由 Agent 调用 plugin_manager remove_bundle，target=@local/gov-pipeline。'
Write-Output '此脚本不直接修改运行中的 profile；源文件、旧 .agent-presets 和业务案件均不删除。'
