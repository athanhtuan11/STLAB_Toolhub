# Nap firmware may bom vao ESP32 bang 1 lenh: build (neu can) -> nap -> mo Serial monitor (xem ma QR ket noi app).
#   powershell -ExecutionPolicy Bypass -File flash.ps1                 # COM5, nap + monitor
#   powershell -ExecutionPolicy Bypass -File flash.ps1 -Port COM7      # doi cong
#   powershell -ExecutionPolicy Bypass -File flash.ps1 -Erase          # xoa sach flash truoc (mat Wi-Fi + lien ket app)
#   powershell -ExecutionPolicy Bypass -File flash.ps1 -NoMonitor      # nap xong thoat
# Hoac bam dup flash.bat. Monitor: thoat bang Ctrl+].
# AN TOAN: cam USB nap code thi NGAT nguon 5 V cua tu (DevKitC: chi 1 nguon tai 1 luc).
param(
    [string]$Port = "COM5",
    [switch]$Erase,
    [switch]$NoMonitor
)
# Khong dung $ErrorActionPreference = "Stop": PowerShell 5.1 coi chu in ra stderr cua idf.py/python la loi -> dung sai.
# Kiem $LASTEXITCODE sau moi buoc.
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"   # ESP-IDF 5.5.4 trong C:\Espressif
. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
Set-Location $PSScriptRoot

Write-Host "== Build ==" -ForegroundColor Cyan
idf.py build
if ($LASTEXITCODE -ne 0) { Write-Host "BUILD LOI" -ForegroundColor Red; exit 1 }

if ($Erase) {
    Write-Host "== Xoa flash ($Port) ==" -ForegroundColor Yellow
    idf.py -p $Port erase-flash
    if ($LASTEXITCODE -ne 0) { Write-Host "XOA FLASH LOI" -ForegroundColor Red; exit 1 }
}

Write-Host "== Nap vao $Port ==" -ForegroundColor Cyan
idf.py -p $Port flash
if ($LASTEXITCODE -ne 0) {
    Write-Host "NAP LOI: kiem cong $Port (Device Manager), cap USB, giu nut BOOT khi bat dau nap neu can" -ForegroundColor Red
    exit 1
}
Write-Host "NAP XONG" -ForegroundColor Green

if (-not $NoMonitor) {
    Write-Host "== Monitor (Ctrl+] de thoat): tim ma QR / PROV_xxxx de them thiet bi trong app ==" -ForegroundColor Cyan
    idf.py -p $Port monitor
}
