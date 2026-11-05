# Build firmware do ESP32-A1S bang ESP-IDF 5.5.4 (C:\Espressif). Xoa bien MSYS (Git Bash lam idf.py tu choi chay)
# va xoa .bin cu truoc khi build de gate khong PASS gia.
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"
Set-Location $PSScriptRoot
foreach ($v in 'MSYSTEM', 'MSYSTEM_PREFIX', 'MSYSTEM_CHOST', 'MINGW_PREFIX', 'MSYS', 'CHERE_INVOKING') {
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}
Remove-Item build\probe_a1s.bin -ErrorAction SilentlyContinue
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
idf.py set-target esp32 *> build-target.log
idf.py build *> build.log
$code = $LASTEXITCODE
Get-Content build.log -Tail 15
if (-not (Test-Path build\probe_a1s.bin)) { Write-Host "BUILD LOI: khong co build\probe_a1s.bin"; if (-not $code) { $code = 1 } }
if ($null -eq $code) { $code = 1 }
exit $code
