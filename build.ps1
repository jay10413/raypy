$ErrorActionPreference = "Stop"

$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY = "1"

Write-Host "Building Rust module with maturin..."
maturin build --release

# Find the latest wheel
$wheel = Get-ChildItem -Path ".\target\wheels" -Filter "*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$wheelName = $wheel.Name
$wheelFullPath = $wheel.FullName

# Ensure dist folder exists and copy wheel there
if (-Not (Test-Path ".\dist")) { New-Item -ItemType Directory -Path ".\dist" | Out-Null }
Copy-Item $wheelFullPath -Destination ".\dist\" -Force
$wheelDistPath = ".\dist\$wheelName"

# Temporary extraction folder (same as wheel name without .whl)
$tempDirName = [System.IO.Path]::GetFileNameWithoutExtension($wheelName)
$tempDir = Join-Path $env:TEMP $tempDirName

# Clean temp folder if exists
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir }
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Extract the wheel
Write-Host "Extracting wheel..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($wheelDistPath, $tempDir)

# Find the raypy/ folder inside extracted wheel
$raypyFolder = Get-ChildItem -Path $tempDir -Recurse -Directory | Where-Object { $_.Name -eq "raypy" } | Select-Object -First 1
if (-not $raypyFolder) { throw "raypy folder not found in extracted wheel!" }

# Patch Python files: append contents of all .py files in patches/ into __init__.py
# BEFORE appending, replace circular imports inside patches:
#   from patches.* -> from raypy import *
$initFile = Join-Path $raypyFolder.FullName "__init__.py"
$patchFiles = Get-ChildItem -Path ".\patches" -Recurse -Filter "*.py"

foreach ($patch in $patchFiles) {
    Write-Host "Patching: $($patch.Name)"

    # Read patch file
    $lines = Get-Content $patch.FullName

    # Replace any 'from patches.* import' with 'from raypy import'
    $linesFixed = $lines | ForEach-Object {
        $_ -replace "^from patches\.(.*) import", "from raypy import `$1"
    }

    # Append to __init__.py
    $linesFixed | Add-Content $initFile
}

# Repack the wheel
Write-Host "Repacking wheel..."
Remove-Item $wheelDistPath -Force
[System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $wheelDistPath)

# Clean up temp folder
Remove-Item -Recurse -Force $tempDir

# Install the patched wheel
Write-Host "Installing patched wheel..."
pip install --upgrade $wheelDistPath

# Run example
Write-Host "Running example script..."
python ".\examples\main.py"
