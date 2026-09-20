Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GovPipelineContext {
    param([string]$DshHome)
    $repoRoot = Split-Path -Parent $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($DshHome)) {
        if (-not [string]::IsNullOrWhiteSpace($env:DSH_HOME)) { $DshHome = $env:DSH_HOME }
        else { $DshHome = Join-Path $HOME '.dsh' }
    }
    $source = Join-Path $repoRoot 'distribution\gov-pipeline'
    $presetRoot = Join-Path $DshHome '.agent-presets'
    $target = Join-Path $presetRoot 'gov-pipeline'
    [pscustomobject]@{ RepoRoot=$repoRoot; DshHome=$DshHome; Source=$source; PresetRoot=$presetRoot; Target=$target }
}

function Assert-GovPipelineSource {
    param($Context)
    foreach ($relative in @('agent.cordis.yml','preset.yml','skills\responsibility-decomposition\SKILL.md','skills\digital-support-analysis\SKILL.md','skills\swimlane-generation\SKILL.md','skills\governance-pipeline\SKILL.md')) {
        $path = Join-Path $Context.Source $relative
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "缺少发布源文件：$path" }
    }
}

function Get-TreeDigest {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { return $null }
    $rows = Get-ChildItem -LiteralPath $Path -File -Recurse | Where-Object { $_.Name -ne 'pipeline-root.txt' } | Sort-Object FullName | ForEach-Object {
        $relative = $_.FullName.Substring($Path.Length).TrimStart('\')
        "$relative`t$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash)"
    }
    $text = $rows -join "`n"
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
        ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()
    } finally { $sha.Dispose() }
}
