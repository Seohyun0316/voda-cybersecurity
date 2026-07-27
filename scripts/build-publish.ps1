param(
    [switch]$SkipInstall,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$PublishRoot = Join-Path $RepoRoot "publish"
$ExtensionRoot = Join-Path $RepoRoot "extension"
$ServerRoot = Join-Path $RepoRoot "server"
$PackagingRoot = Join-Path $RepoRoot "packaging"

function Assert-InRepo {
    param([string]$Path)

    $FullPath = [System.IO.Path]::GetFullPath($Path)
    $RepoPrefix = $RepoRoot.TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    ) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $FullPath.StartsWith($RepoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "The build path is outside the repository: $FullPath"
    }
}

function Assert-NativeSuccess {
    param([string]$Message)

    if ($LASTEXITCODE -ne 0) {
        throw "$Message (exit code: $LASTEXITCODE)"
    }
}

Assert-InRepo $PublishRoot

$PackageJson = Get-Content -Raw -Encoding utf8 (Join-Path $ExtensionRoot "package.json") |
    ConvertFrom-Json
$Version = [string]$PackageJson.version
if (-not $Version) {
    throw "Unable to determine the Extension version."
}

if (Test-Path -LiteralPath $PublishRoot) {
    $ResolvedPublish = (Resolve-Path -LiteralPath $PublishRoot).Path
    Assert-InRepo $ResolvedPublish
    Get-ChildItem -LiteralPath $ResolvedPublish -Force | Remove-Item -Recurse -Force
}
else {
    New-Item -ItemType Directory -Path $PublishRoot | Out-Null
}

if (-not $SkipInstall) {
    Write-Host "[VibeSafe] Installing Extension dependencies with npm ci..."
    Push-Location $ExtensionRoot
    try {
        & npm ci
        Assert-NativeSuccess "npm ci failed."
    }
    finally {
        Pop-Location
    }
}

if (-not $SkipTests) {
    Write-Host "[VibeSafe] Running Extension tests..."
    Push-Location $ExtensionRoot
    try {
        & npm test
        Assert-NativeSuccess "Extension tests failed."
    }
    finally {
        Pop-Location
    }

    Write-Host "[VibeSafe] Running backend tests..."
    Push-Location $ServerRoot
    try {
        & python -B -m pytest -p no:cacheprovider -q
        Assert-NativeSuccess "Backend tests failed."
    }
    finally {
        Pop-Location
    }
}

$VsixName = "VibeSafe-$Version.vsix"
$VsixPath = Join-Path $PublishRoot $VsixName
Write-Host "[VibeSafe] Building the VSIX..."
Push-Location $ExtensionRoot
try {
    & npm run package:vsix -- --out $VsixPath
    Assert-NativeSuccess "VSIX packaging failed."
}
finally {
    Pop-Location
}

$BackendRoot = Join-Path $PublishRoot "backend"
Assert-InRepo $BackendRoot
New-Item -ItemType Directory -Path $BackendRoot | Out-Null

Copy-Item -LiteralPath (Join-Path $ServerRoot "app.py") -Destination $BackendRoot
Copy-Item -LiteralPath (Join-Path $ServerRoot "requirements.txt") -Destination $BackendRoot
Copy-Item -Path (Join-Path $PackagingRoot "backend\*") -Destination $BackendRoot -Recurse

$BackendSourceFiles = Get-ChildItem -LiteralPath (Join-Path $ServerRoot "vibesafe") -Recurse -File |
    Where-Object { $_.Extension -eq ".py" }
foreach ($SourceFile in $BackendSourceFiles) {
    $ServerPrefix = $ServerRoot.TrimEnd("\", "/") + "\"
    if (-not $SourceFile.FullName.StartsWith(
        $ServerPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "A backend source path is outside the server folder: $($SourceFile.FullName)"
    }
    $RelativePath = $SourceFile.FullName.Substring($ServerPrefix.Length)
    $Destination = Join-Path $BackendRoot $RelativePath
    $DestinationDirectory = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $DestinationDirectory -Force | Out-Null
    Copy-Item -LiteralPath $SourceFile.FullName -Destination $Destination
}

$RulesetDestination = Join-Path $BackendRoot "config"
$ModelDestination = Join-Path $BackendRoot "models\xgboost_10f"
New-Item -ItemType Directory -Path $RulesetDestination -Force | Out-Null
New-Item -ItemType Directory -Path $ModelDestination -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $ServerRoot "config\ruleset.toml") -Destination $RulesetDestination
Copy-Item -LiteralPath (Join-Path $ServerRoot "models\xgboost_10f\model.json") -Destination $ModelDestination
Copy-Item -LiteralPath (Join-Path $ServerRoot "models\xgboost_10f\metadata.json") -Destination $ModelDestination

Write-Host "[VibeSafe] Verifying the copied backend..."
Push-Location $BackendRoot
try {
    & python -B -c "from vibesafe.api import create_app; app = create_app(); response = app.test_client().get('/health'); assert response.status_code == 200; assert response.get_json()['status'] == 'ok'"
    Assert-NativeSuccess "Copied backend verification failed."
}
finally {
    Pop-Location
}

$BackendZipName = "VibeSafe-backend-$Version.zip"
$BackendZipPath = Join-Path $PublishRoot $BackendZipName
Compress-Archive -LiteralPath $BackendRoot -DestinationPath $BackendZipPath -CompressionLevel Optimal

$ReadmeTemplate = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $PackagingRoot "publish-README.md")
$ReadmeTemplate.Replace("{{VERSION}}", $Version) |
    Set-Content -Encoding utf8 (Join-Path $PublishRoot "README.md")

$UserGuideName = "USER-GUIDE.md"
$UserGuideTemplate = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $PackagingRoot "user-guide.md")
$UserGuideTemplate.Replace("{{VERSION}}", $Version) |
    Set-Content -Encoding utf8 (Join-Path $PublishRoot $UserGuideName)

$GitCommit = (& git -C $RepoRoot rev-parse HEAD).Trim()
Assert-NativeSuccess "Unable to determine the Git commit."
$GitStatus = @(& git -C $RepoRoot status --porcelain)
Assert-NativeSuccess "Unable to determine the Git status."

$Manifest = [ordered]@{
    product = "VibeSafe"
    version = $Version
    built_at_utc = [DateTime]::UtcNow.ToString("o")
    git_commit = $GitCommit
    working_tree_clean = ($GitStatus.Count -eq 0)
    backend_bind = "127.0.0.1:38457"
    artifacts = @($VsixName, $BackendZipName)
}
$Manifest | ConvertTo-Json -Depth 4 |
    Set-Content -Encoding utf8 (Join-Path $PublishRoot "release-manifest.json")

$ChecksumLines = foreach ($ArtifactPath in @($VsixPath, $BackendZipPath)) {
    $Hash = Get-FileHash -Algorithm SHA256 -LiteralPath $ArtifactPath
    "{0}  {1}" -f $Hash.Hash.ToLowerInvariant(), (Split-Path -Leaf $ArtifactPath)
}
$ChecksumLines | Set-Content -Encoding ascii (Join-Path $PublishRoot "SHA256SUMS.txt")

Write-Host ""
Write-Host "[VibeSafe] Release artifacts are ready:"
Get-ChildItem -LiteralPath $PublishRoot |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize
