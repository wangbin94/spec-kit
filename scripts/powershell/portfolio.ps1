param(
    [switch]$Json,
    [switch]$NoWrite,
    [switch]$Help
)

function Show-Help {
    @'
Usage: portfolio.ps1 [--Json] [--NoWrite]

Summarise Spec Kit features and update .specify/state/features.yaml.
    --Json     Output JSON instead of a table
    --NoWrite  Skip writing the registry file (diagnostic only)
    --Help     Show this help message
'@
}

if ($Help) {
    Show-Help
    exit 0
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path (Split-Path $scriptDir -Parent) 'portfolio.py'

if (-not (Test-Path $pythonScript)) {
    Write-Error "portfolio.py not found at $pythonScript"
    exit 1
}

$python = $env:PYTHON
if (-not $python) { $python = 'python3' }
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    Write-Error "python3 is required to run the portfolio summary"
    exit 1
}

$argsList = @($python, $pythonScript)
if ($Json)    { $argsList += '--json' }
if ($NoWrite) { $argsList += '--no-write' }

& $argsList[0] $argsList[1..($argsList.Length - 1)]
exit $LASTEXITCODE
