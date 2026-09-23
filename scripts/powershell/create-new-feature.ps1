#!/usr/bin/env pwsh
# Create Spec Kit feature files from the CURRENT Git branch.
#
# IMPORTANT:
# - This script DOES NOT create, switch, rename, merge, or delete Git branches.
# - Git branch management is external to this script.
# - The current Git branch name becomes the Spec Kit feature name.
#
# Example:
#   Current Git branch: 003-user-auth
#   FEATURE_NAME:       003-user-auth
#   FEATURE_DIR:        specs/003-user-auth

[CmdletBinding()]
param(
    [switch]$Json,

    [Alias('AllowExistingBranch')]
    [switch]$AllowExistingFeature,

    [switch]$DryRun,

    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Host "Usage: ./create-new-feature.ps1 [-Json] [-DryRun] [-AllowExistingFeature]"
    Write-Host ""
    Write-Host "Purpose:"
    Write-Host "  Read the current Git branch name and create the matching Spec Kit feature directory."
    Write-Host ""
    Write-Host "This script DOES NOT manage Git."
    Write-Host "It never creates, switches, renames, merges, or deletes branches."
    Write-Host ""
    Write-Host "Expected branch examples:"
    Write-Host "  003-user-auth"
    Write-Host "  014-product-review"
    Write-Host "  20260923-134500-payment-flow"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Json                  Output machine-readable JSON"
    Write-Host "  -DryRun                Compute names/paths without creating files"
    Write-Host "  -AllowExistingFeature  Reuse an existing feature directory"
    Write-Host "  -Help                  Show this help message"
    exit 0
}

# Shared Spec Kit helpers.
. "$PSScriptRoot/common.ps1"

$repoRoot = Get-RepoRoot
Set-Location $repoRoot

# Git is used only to READ repository/branch state.
$insideGitOutput = & git rev-parse --is-inside-work-tree 2>$null
$insideGitExitCode = $LASTEXITCODE
$insideGit = [string]($insideGitOutput | Select-Object -First 1)

if ($insideGitExitCode -ne 0 -or $insideGit.Trim() -ne 'true') {
    Write-Error "Spec Kit could not read a Git repository. Select/open the project repository first."
    exit 1
}

$branchOutput = & git branch --show-current 2>$null
$branchExitCode = $LASTEXITCODE
$currentBranch = [string]($branchOutput | Select-Object -First 1)
$currentBranch = $currentBranch.Trim()

if ($branchExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($currentBranch)) {
    Write-Error "Spec Kit could not determine the current Git branch. Checkout a feature branch first."
    exit 1
}

# Keep branch name and feature directory basename identical.
# Branch names containing '/' or '\' are rejected instead of rewritten.
if ($currentBranch -match '[/\\]') {
    Write-Error "Current Git branch '$currentBranch' contains a path separator. Spec Kit requires a single feature name such as '003-user-auth' so the branch name and feature directory basename remain identical."
    exit 1
}

# Spec Kit feature branches must carry their feature identifier.
#
# Supported:
#   sequential: NNN-short-name
#   timestamp:  YYYYMMDD-HHMMSS-short-name
#
# The suffix must be kebab-like: words separated by single hyphens.
$numberingMode = $null
$featureNum = $null
$namePartPattern = '[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*'

if ($currentBranch -match "^(\d{8}-\d{6})-($namePartPattern)$") {
    $numberingMode = 'timestamp'
    $featureNum = $matches[1]
}
elseif ($currentBranch -match "^(\d{3,})-($namePartPattern)$") {
    $numberingMode = 'sequential'
    $featureNum = $matches[1]
}
else {
    Write-Error "Current Git branch '$currentBranch' is not a Spec Kit feature branch. Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'."
    exit 1
}

$featureName = $currentBranch
$branchName = $currentBranch

$specsDir = Join-Path $repoRoot 'specs'
$featureDir = Join-Path $specsDir $featureName
$specFile = Join-Path $featureDir 'spec.md'

$featureDirExists = Test-Path -LiteralPath $featureDir -PathType Container
$specExists = Test-Path -LiteralPath $specFile -PathType Leaf

if ($featureDirExists -and -not $AllowExistingFeature) {
    Write-Error "Feature directory '$featureDir' already exists. Use -AllowExistingFeature only when intentionally reopening the same feature."
    exit 1
}

if (-not $DryRun) {
    $templateContent = $null

    if (-not $specExists) {
        $templateContent = Resolve-TemplateContent `
            -TemplateName 'spec-template' `
            -RepoRoot $repoRoot
    }

    New-Item -ItemType Directory -Path $specsDir -Force | Out-Null
    New-Item -ItemType Directory -Path $featureDir -Force | Out-Null

    if (-not $specExists) {
        if ($null -ne $templateContent) {
            $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText(
                $specFile,
                $templateContent,
                $utf8NoBom
            )
        }
        else {
            [Console]::Error.WriteLine(
                "[specify] Warning: spec-template was not found; created an empty spec.md."
            )

            New-Item -ItemType File -Path $specFile -Force | Out-Null
        }
    }

    # Downstream Spec Kit commands resolve the active feature from feature.json.
    # Pass a forward-slash relative path so the stored value matches the bash
    # and python twins (Join-Path-free, portable in JSON).
    Save-FeatureJson `
        -RepoRoot $repoRoot `
        -FeatureDirectory "specs/$featureName"

    # Convenience values for commands executed in this PowerShell process.
    $env:SPECIFY_FEATURE = $featureName
    $env:SPECIFY_FEATURE_DIRECTORY = $featureDir
}

$result = [PSCustomObject]@{
    FEATURE_NAME   = $featureName
    BRANCH_NAME    = $branchName
    FEATURE_NUM    = $featureNum
    FEATURE_DIR    = $featureDir
    SPEC_FILE      = $specFile
    NUMBERING_MODE = $numberingMode
}

if ($DryRun) {
    $result | Add-Member `
        -NotePropertyName 'DRY_RUN' `
        -NotePropertyValue $true
}

if ($Json) {
    $result | ConvertTo-Json -Compress
}
else {
    Write-Output "FEATURE_NAME: $featureName"
    Write-Output "BRANCH_NAME: $branchName"
    Write-Output "FEATURE_NUM: $featureNum"
    Write-Output "FEATURE_DIR: $featureDir"
    Write-Output "SPEC_FILE: $specFile"
    Write-Output "NUMBERING_MODE: $numberingMode"
}
