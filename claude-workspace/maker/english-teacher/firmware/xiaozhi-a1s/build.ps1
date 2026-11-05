# Build xiaozhi cho STLab A1S bang ESP-IDF 6.1 (xoa bien MSYS vi Git Bash lam idf.py tu choi chay).
$ErrorActionPreference = 'Stop'
$H = $PSScriptRoot
foreach ($v in 'MSYSTEM','MSYSTEM_PREFIX','MSYSTEM_CHOST','MINGW_PREFIX','MSYS','CHERE_INVOKING') {
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}
$env:IDF_TOOLS_PATH = 'C:\Espressif\tools-v6.1'
. 'C:\Espressif\frameworks\esp-idf-v6.1\export.ps1' | Out-Null

# build-src la junction -> C:\xzb\a1s (xem sync.ps1); chay idf.py tu thu muc that ngan
$Src = 'C:\xzb\a1s'
if (-not (Test-Path (Join-Path $Src 'CMakeLists.txt'))) { throw 'Chua co build-src; chay sync.ps1 truoc' }
Set-Location $Src
Remove-Item -Force (Join-Path $Src 'build\xiaozhi.bin') -ErrorAction SilentlyContinue

$log = Join-Path $H 'build.log'
"" | Set-Content $log
# stderr cua idf.py khong duoc lam PowerShell ngat; ghi tat ca vao log
$ErrorActionPreference = 'Continue'
& cmd /c "idf.py set-target esp32 >> `"$log`" 2>&1"
$rc1 = $LASTEXITCODE
if ($rc1 -eq 0) {
    & cmd /c "idf.py build >> `"$log`" 2>&1"
    $rc1 = $LASTEXITCODE
}
Get-Content $log -Tail 15
Set-Location $H
if ($rc1 -ne 0 -or -not (Test-Path (Join-Path $Src 'build\xiaozhi.bin'))) {
    Write-Error 'Build that bai hoac thieu build\xiaozhi.bin'
    exit 1
}
Write-Host "BUILD OK $((Get-Item (Join-Path $Src 'build\xiaozhi.bin')).Length) bytes"
exit 0
