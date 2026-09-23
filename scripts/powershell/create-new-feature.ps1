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
#
# When the current branch is not a valid feature branch (or no branch can be
# read, e.g. detached HEAD), the script exits with code 3 and -Json output
# contains {"ACTION": "ASK_USER_FOR_FEATURE_NAME", ...}. The caller can then
# re-run with -FeatureName <name> to set the feature name explicitly.
# A bare kebab name (e.g. "user-auth") is auto-numbered by scanning specs/
# for the next sequential number (e.g. "001-user-auth").

[CmdletBinding()]
param(
    [switch]$Json,

    [Alias('AllowExistingBranch')]
    [switch]$AllowExistingFeature,

    [switch]$DryRun,

    [string]$FeatureName = '',

    [switch]$Help
)

$ErrorActionPreference = 'Stop'

if ($Help) {
    Write-Host "Usage: ./create-new-feature.ps1 [-Json] [-DryRun] [-AllowExistingFeature] [-FeatureName <name>]"
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
    Write-Host "  -FeatureName <name>    Set the feature name explicitly (overrides the branch)."
    Write-Host "                         Accepts '003-user-auth', 'YYYYMMDD-HHMMSS-user-auth',"
    Write-Host "                         or a bare kebab name such as 'user-auth' (auto-numbered"
    Write-Host "                         by scanning specs/ for the next sequential number)"
    Write-Host "  -Help                  Show this help message"
    Write-Host ""
    Write-Host "Exit codes:"
    Write-Host "  0  success"
    Write-Host "  1  hard error (bad options, invalid -FeatureName, template failure)"
    Write-Host "  3  feature name required: re-run with -FeatureName <name>; -Json output"
    Write-Host '     contains {"ACTION": "ASK_USER_FOR_FEATURE_NAME", ...}'
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

# Spec Kit feature names must carry their feature identifier.
#
# Supported:
#   sequential: NNN-short-name
#   timestamp:  YYYYMMDD-HHMMSS-short-name
#
# The suffix must be kebab-like: words separated by single hyphens.
$namePartPattern = '[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*'

# Exit-3 path: a recoverable failure solved by -FeatureName.
function Ask-UserForFeatureNameRequired {
    param(
        [string]$Message,
        [string]$BranchName
    )
    [Console]::Error.WriteLine($Message)
    if ($Json) {
        $askPayload = [ordered]@{
            ACTION     = 'ASK_USER_FOR_FEATURE_NAME'
            ERROR      = $Message
            BRANCH_NAME = $BranchName
        }
        [PSCustomObject]$askPayload | ConvertTo-Json -Compress
    }
    exit 3
}

# Global maximum NNN- prefix in specs/ plus one (timestamp dirs excluded).
function Get-NextFeatureNumber {
    param([string]$SpecsDir)

    $maxNum = 0
    if (Test-Path -LiteralPath $SpecsDir -PathType Container) {
        foreach ($entry in (Get-ChildItem -LiteralPath $SpecsDir -Directory)) {
            if ($entry.Name -match '^[0-9]{8}-[0-9]{6}-') {
                # Timestamp-shaped names carry no sequential number.
                continue
            }
            if ($entry.Name -match '^([0-9]{3,})-') {
                $parsed = [long]::Parse(
                    $Matches[1],
                    [System.Globalization.CultureInfo]::InvariantCulture
                )
                if ($parsed -gt $maxNum) {
                    $maxNum = $parsed
                }
            }
        }
    }
    return $maxNum + 1
}

$specsDir = Join-Path $repoRoot 'specs'
$explicitName = ''
if ($null -ne $FeatureName) {
    $explicitName = $FeatureName.Trim()
}

$numberingMode = $null
$featureNum = $null

if ($explicitName -ne '') {
    # Explicit -FeatureName overrides the branch-derived name.
    if ($explicitName -match '[/\\]') {
        Write-Error "Feature name '$explicitName' contains a path separator. Provide a single name such as '003-user-auth' or a bare kebab name such as 'user-auth'."
        exit 1
    }

    if ($explicitName -match "^(\d{8}-\d{6})-($namePartPattern)$") {
        $numberingMode = 'timestamp'
        $featureNum = $Matches[1]
        $featureName = $explicitName
    }
    elseif ($explicitName -match "^(\d{3,})-($namePartPattern)$") {
        $numberingMode = 'sequential'
        $featureNum = $Matches[1]
        $featureName = $explicitName
    }
    elseif ($explicitName -match "^($namePartPattern)$") {
        $nextNum = Get-NextFeatureNumber -SpecsDir $specsDir
        $featureNum = $nextNum.ToString('D3')
        $featureName = "$featureNum-$explicitName"
        $numberingMode = 'sequential'
    }
    else {
        Write-Error "Feature name '$explicitName' is not a valid Spec Kit feature name. Expected '003-user-auth', 'YYYYMMDD-HHMMSS-user-auth', or a bare kebab name such as 'user-auth'."
        exit 1
    }

    $branchName = $currentBranch
}
else {
    if ($branchExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($currentBranch)) {
        Ask-UserForFeatureNameRequired `
            -Message 'Spec Kit could not determine the current Git branch. Checkout a feature branch first, or re-run with --feature-name <name>.' `
            -BranchName ''
    }

    # Keep branch name and feature directory basename identical.
    # Branch names containing '/' or '\' are rejected instead of rewritten.
    if ($currentBranch -match '[/\\]') {
        Ask-UserForFeatureNameRequired `
            -Message "Current Git branch '$currentBranch' contains a path separator. Spec Kit requires a single feature name such as '003-user-auth' so the branch name and feature directory basename remain identical. Re-run with --feature-name <name> to set the feature name explicitly." `
            -BranchName $currentBranch
    }

    if ($currentBranch -match "^(\d{8}-\d{6})-($namePartPattern)$") {
        $numberingMode = 'timestamp'
        $featureNum = $matches[1]
    }
    elseif ($currentBranch -match "^(\d{3,})-($namePartPattern)$") {
        $numberingMode = 'sequential'
        $featureNum = $matches[1]
    }
    else {
        Ask-UserForFeatureNameRequired `
            -Message "Current Git branch '$currentBranch' is not a Spec Kit feature branch. Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'. Re-run with --feature-name <name> to set the feature name explicitly." `
            -BranchName $currentBranch
    }

    $featureName = $currentBranch
    $branchName = $currentBranch
}

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
