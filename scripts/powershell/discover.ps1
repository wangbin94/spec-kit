param(
    [switch]$Json,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

function Show-Help {
@"
Usage: discover.ps1 [--Json] <idea description>

Create a backlog intake stub for a new idea and return its file path.
"@
}

if ($Help) {
    Show-Help
    exit 0
}

$ideaDescription = ($Args -join ' ').Trim()
if (-not $ideaDescription) {
    Write-Error "Idea description required."
    Show-Help
    exit 1
}

function Find-RepoRoot([string]$start) {
    $dir = Get-Item -LiteralPath $start
    while ($dir -ne $null) {
        if (Test-Path (Join-Path $dir.FullName '.specify') -PathType Container -or
            Test-Path (Join-Path $dir.FullName '.git') -PathType Container) {
            return $dir.FullName
        }
        $dir = $dir.Parent
    }
    return $null
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Find-RepoRoot $scriptDir
if (-not $repoRoot) {
    Write-Error "Could not locate repository root."
    exit 1
}

$backlogDir = Join-Path $repoRoot 'backlog'
if (-not (Test-Path $backlogDir)) { New-Item -ItemType Directory -Path $backlogDir | Out-Null }

$highest = 0
Get-ChildItem -LiteralPath $backlogDir -Directory | ForEach-Object {
    if ($_.Name -match '^I([0-9]{3})-') {
        $n = [int]$matches[1]
        if ($n -gt $highest) { $highest = $n }
    }
}

$next = $highest + 1
$ideaNum = "I{0:D3}" -f $next

function Convert-ToSlug([string]$text) {
    $lower = $text.ToLowerInvariant()
    $slug = [regex]::Replace($lower, '[^a-z0-9]', '-')
    $slug = [regex]::Replace($slug, '-{2,}', '-').Trim('-')
    if (-not $slug) { $slug = 'idea' }
    return $slug
}

$slug = Convert-ToSlug $ideaDescription
$ideaDir = Join-Path $backlogDir ("$ideaNum-$slug")
if (-not (Test-Path $ideaDir)) { New-Item -ItemType Directory -Path $ideaDir | Out-Null }

$template = Join-Path $repoRoot '.specify/templates/intake-template.md'
$intakeFile = Join-Path $ideaDir 'intake.md'

if (Test-Path $template) {
    Copy-Item $template $intakeFile -Force
} else {
    @"
# Idea Intake

## Overview
- **Idea ID:**
- **Working Title:**
- **Problem / Opportunity:**
- **Target Users / Stakeholders:**

## Goals & Outcomes
- Primary objectives
- Success metrics or signals

## Scope
- In scope
- Out of scope / deferrals

## Constraints & Assumptions
- Technical constraints
- Policy, compliance, or organisational limits

## Risks & Unknowns
- Major risks
- Open questions / research needed

## Proposed Approach (Optional)
- Initial ideas to explore

## Next Steps
- Decision / recommendation (proceed, research more, drop)
- Follow-up actions or owners

"@ | Set-Content -LiteralPath $intakeFile -Encoding UTF8
}

if ($Json) {
    $payload = @{ IDEA_ID = $ideaNum; IDEA_DIR = $ideaDir; INTAKE_FILE = $intakeFile }
    $payload | ConvertTo-Json -Compress
} else {
    Write-Output "IDEA_ID: $ideaNum"
    Write-Output "IDEA_DIR: $ideaDir"
    Write-Output "INTAKE_FILE: $intakeFile"
}
