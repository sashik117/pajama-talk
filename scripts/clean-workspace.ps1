param(
    [switch]$Deep,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Get-PathSizeMb {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }
    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer) {
        return [math]::Round(($item.Length / 1MB), 2)
    }
    $sum = (Get-ChildItem -LiteralPath $Path -Force -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    return [math]::Round(($sum / 1MB), 2)
}

function Remove-KnownPath {
    param([string]$RelativePath)
    $target = Join-Path $root $RelativePath
    if (-not (Test-Path -LiteralPath $target)) {
        return 0
    }
    $resolved = (Resolve-Path -LiteralPath $target).Path
    if (-not $resolved.StartsWith($root)) {
        throw "Refusing to remove path outside workspace: $resolved"
    }
    $size = Get-PathSizeMb $resolved
    if ($WhatIf) {
        Write-Host "Would remove $RelativePath ($size MB)"
    } else {
        try {
            Remove-Item -LiteralPath $resolved -Recurse -Force
            Write-Host "Removed $RelativePath ($size MB)"
        } catch [System.IO.IOException] {
            Write-Host "Skipped locked $RelativePath ($size MB)"
            return 0
        }
    }
    return $size
}

$targets = @(
    ".tmp",
    ".pytest_cache",
    "backend\.pytest_cache",
    "frontend\.gradle-home",
    "frontend\.gradle",
    "frontend\build",
    "frontend\androidApp\build",
    "frontend\desktopApp\build",
    "frontend\shared\build",
    "web\dist",
    "web\test-results",
    "web\playwright-report",
    "web\tsconfig.tsbuildinfo"
)

if ($Deep) {
    $targets += @(
        ".gradle-home",
        "backend\.venv",
        "web\node_modules"
    )
}

$freed = 0
foreach ($target in $targets) {
    $freed += Remove-KnownPath $target
}

$pycacheRoots = @("backend\app", "backend\tests")
if ($Deep) {
    $pycacheRoots += "backend\.venv"
}

foreach ($pycacheRoot in $pycacheRoots) {
    $scanRoot = Join-Path $root $pycacheRoot
    if (-not (Test-Path -LiteralPath $scanRoot)) {
        continue
    }
    $pycacheDirs = Get-ChildItem -LiteralPath $scanRoot -Force -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName.StartsWith($root) }
    foreach ($dir in $pycacheDirs) {
        $relative = $dir.FullName.Substring($root.Length + 1)
        $freed += Remove-KnownPath $relative
    }
}

if ($WhatIf) {
    Write-Host "Would free about $([math]::Round($freed, 2)) MB."
} else {
    Write-Host "Freed about $([math]::Round($freed, 2)) MB."
}
