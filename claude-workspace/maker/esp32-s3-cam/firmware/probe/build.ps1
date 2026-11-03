# Build firmware do (probe) bang ESP-IDF 5.5.4 cai trong C:\Espressif (giong maker/pump-control).
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"
Set-Location $PSScriptRoot
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
idf.py set-target esp32s3 *> build-target.log
idf.py build *> build.log
$code = $LASTEXITCODE
Get-Content build.log -Tail 15
exit $code
