# Build lai + nap firmware guitar_a1s vao ESP32-A1S. Dung: .\flash.ps1 [-Port COM5]
param([string]$Port = "COM5")
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"
Set-Location $PSScriptRoot
foreach ($v in 'MSYSTEM', 'MSYSTEM_PREFIX', 'MSYSTEM_CHOST', 'MINGW_PREFIX', 'MSYS', 'CHERE_INVOKING') {
    Remove-Item "Env:$v" -ErrorAction SilentlyContinue
}
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
idf.py -p $Port flash *> flash.log
$code = $LASTEXITCODE
Get-Content flash.log -Tail 12
exit $code
