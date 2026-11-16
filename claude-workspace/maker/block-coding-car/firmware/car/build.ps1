# Build firmware block-coding-car bang ESP-IDF 5.5.4 (C:\Espressif), mau tu esp32-s3-cam/firmware/cam/build.ps1.
# Goi tu Git Bash ke thua MSYSTEM -> idf.py tu choi chay: xoa bien MSYS + xoa .bin cu truoc khi build.
# Buoc 1: tao main/www/index.html.gz tu app (app/build.py --out); app chua co/loi -> nen main/placeholder.html (WARN).
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"
Set-Location $PSScriptRoot
foreach ($v in 'MSYSTEM', 'MSYSTEM_PREFIX', 'MSYSTEM_CHOST', 'MINGW_PREFIX', 'MSYS', 'CHERE_INVOKING') {
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}

$py = Join-Path $PSScriptRoot "..\.venv-host\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
New-Item -ItemType Directory -Force main\www | Out-Null
$gz = "main\www\index.html.gz"
Remove-Item $gz -ErrorAction SilentlyContinue
$appBuild = Join-Path $PSScriptRoot "..\..\app\build.py"
$appOk = $false
if (Test-Path $appBuild) {
    & $py $appBuild --out $gz *> app-build.log
    if ($LASTEXITCODE -eq 0 -and (Test-Path $gz) -and (Get-Item $gz).Length -gt 0) { $appOk = $true }
}
if (-not $appOk) {
    Write-Host "WARN: app\build.py chua co hoac loi - dung main\placeholder.html thay app"
    Remove-Item $gz -ErrorAction SilentlyContinue
    $code = "import gzip,sys; d=open(r'main\placeholder.html','rb').read(); open(sys.argv[1],'wb').write(gzip.compress(d,9))"
    & $py -c $code $gz
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $gz)) { Write-Host "BUILD LOI: khong tao duoc $gz"; exit 1 }
}

Remove-Item build\block_coding_car.bin -ErrorAction SilentlyContinue
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
idf.py set-target esp32s3 *> build-target.log
idf.py build *> build.log
$code = $LASTEXITCODE
Get-Content build.log -Tail 15
if (-not (Test-Path build\block_coding_car.bin)) { Write-Host "BUILD LOI: khong co build\block_coding_car.bin"; if (-not $code) { $code = 1 } }
if ($null -eq $code) { $code = 1 }
exit $code
