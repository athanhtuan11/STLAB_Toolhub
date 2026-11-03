# Build firmware chinh (cam) bang ESP-IDF 5.5.4 cai trong C:\Espressif (giong maker/pump-control).
# 2026-11-03: goi tu Git Bash (delegate.py) -> ke thua MSYSTEM -> idf.py tu choi "MSys/Mingw is no longer supported"
# ma khong build; stlab_cam.bin cu con lai lam gate PASS gia. Nay: xoa bien MSYS + xoa .bin cu truoc khi build.
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"
Set-Location $PSScriptRoot
foreach ($v in 'MSYSTEM', 'MSYSTEM_PREFIX', 'MSYSTEM_CHOST', 'MINGW_PREFIX', 'MSYS', 'CHERE_INVOKING') {
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}
Remove-Item build\stlab_cam.bin -ErrorAction SilentlyContinue
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
idf.py set-target esp32s3 *> build-target.log
idf.py build *> build.log
$code = $LASTEXITCODE
Get-Content build.log -Tail 15
if (-not (Test-Path build\stlab_cam.bin)) { Write-Host "BUILD LOI: khong co build\stlab_cam.bin"; if (-not $code) { $code = 1 } }
if ($null -eq $code) { $code = 1 }
exit $code
