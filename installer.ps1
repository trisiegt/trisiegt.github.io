#
# PowerShell Script to Install Minecraft Op Manager Components
# Based on the '3ncrypt36c063' pseudocode
#

# --- 1. Get Server Location from User ---
# 'ask-user -prompt "Where is your Minecraft server installed? Give a folder" -outputvar serverlocation'
$serverLocation = Read-Host -Prompt "Where is your Minecraft server installed? (give the full folder path)"

# --- 2. Define Paths and URL ---
$toolsDir = Join-Path -Path $serverLocation -ChildPath "tools"
$targetFile = Join-Path -Path $toolsDir -ChildPath "ops.py"
$cmdFile = Join-Path -Path $serverLocation -ChildPath "opmanager.cmd"
$sourceUrl = "https://trisiegt.github.io/ops.py"

Write-Host "`n> Target directory set: $serverLocation"

try {
    # --- 3. Create the necessary 'tools' directory ---
    if (-not (Test-Path $toolsDir)) {
        Write-Host "> Creating tools directory: $toolsDir"
        # The -Force parameter ensures the parent directory exists, but we rely on $serverLocation being valid.
        New-Item -Path $toolsDir -ItemType Directory -Force | Out-Null
    }

    # --- 4. Download the Python file ---
    # 'call trisiegt.github.io/base64/ops.py And copy-called-file-to-var serverlocation\tools'
    Write-Host "> Downloading ops.py from $sourceUrl to $targetFile..."
    # Use Invoke-WebRequest for downloading, -ErrorAction Stop to catch download failures.
    Invoke-WebRequest -Uri $sourceUrl -OutFile $targetFile -UseBasicParsing -ErrorAction Stop
    Write-Host "> Download Complete! ops.py is ready."

    # --- 5. Write the Command file ---
    # 'write "@cd %~dp0 && @python %~dp0\tools\ops.py && @pause" to serverlocation\opmanager.cmd'
    $cmdContent = "@cd %~dp0 && @python %~dp0\tools\ops.py && @pause"

    Write-Host "> Creating opmanager.cmd at $cmdFile..."
    # Using Out-File with ASCII encoding is recommended for .cmd/.bat files.
    $cmdContent | Out-File -FilePath $cmdFile -Encoding ASCII -Force
    Write-Host "> opmanager.cmd created successfully."
    
    Write-Host "`n>> All done! You can now run '$cmdFile' in your server folder."

} catch {
    Write-Error "`n[ERROR] Something went wrong during installation:"
    Write-Error "Make sure the server location path is correct and you have internet access."
    Write-Error $_
}
