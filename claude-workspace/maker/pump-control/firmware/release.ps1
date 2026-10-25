# Phat hanh firmware moi cho khach cap nhat tu xa (nut "Cap nhat" tren app RainMaker).
#   powershell -ExecutionPolicy Bypass -File release.ps1 -Version 1.1.1 -Notes "Them den bao loi"
# Lam: kiem phien ban moi hon -> ghi PROJECT_VER -> build -> chep .bin + manifest.json vao releases/ -> git commit + push.
# ESP32 doc manifest tu raw.githubusercontent.com (repo PUBLIC) moi 6 gio / sau khoi dong 90 s; cache GitHub ~5 phut.
# Ban moi loi khong len duoc cloud -> sau 90 s tu quay ve ban cu (rollback). Firmware KHONG chua mat khau/khoa.
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$Notes = ""
)
$IdfId = "esp-idf-20ee62e792ea89630ac6a777ab3ebc57"   # ESP-IDF 5.5.4 trong C:\Espressif
$Raw = "https://raw.githubusercontent.com/athanhtuan11/STLAB_Toolhub/main/claude-workspace/maker/pump-control/firmware/releases"
Set-Location $PSScriptRoot

if ($Version -notmatch '^\d+\.\d+\.\d+$') { Write-Host "Phien ban phai dang x.y.z (vd 1.1.1)" -ForegroundColor Red; exit 1 }
$cm = Get-Content CMakeLists.txt -Raw
if ($cm -notmatch 'set\(PROJECT_VER "(\d+\.\d+\.\d+)"\)') { Write-Host "Khong thay PROJECT_VER trong CMakeLists.txt" -ForegroundColor Red; exit 1 }
$old = $Matches[1]
if ([version]$Version -le [version]$old) { Write-Host "Phien ban $Version phai lon hon $old" -ForegroundColor Red; exit 1 }
if ($Notes.Length -gt 80) { $Notes = $Notes.Substring(0, 80) }   # o "Ban moi" tren app ngan

$cm = $cm -replace 'set\(PROJECT_VER "\d+\.\d+\.\d+"\)', "set(PROJECT_VER `"$Version`")"
[IO.File]::WriteAllText("$PSScriptRoot\CMakeLists.txt", $cm)

. C:\Espressif\Initialize-Idf.ps1 -IdfId $IdfId *> $null
Write-Host "== Build $Version ==" -ForegroundColor Cyan
idf.py build
if ($LASTEXITCODE -ne 0) {
    Write-Host "BUILD LOI - tra lai phien ban $old" -ForegroundColor Red
    git checkout -- CMakeLists.txt
    exit 1
}

New-Item -ItemType Directory -Force releases | Out-Null
Get-ChildItem releases -Filter "pump_control-*.bin" | Remove-Item   # chi giu ban moi nhat (lich su con trong git)
$bin = "pump_control-$Version.bin"
Copy-Item build\pump_control.bin "releases\$bin"
$sha = (Get-FileHash "releases\$bin" -Algorithm SHA256).Hash.ToLower()
$manifest = [ordered]@{
    version = $Version
    url     = "$Raw/$bin"
    notes   = $Notes
    date    = (Get-Date -Format "yyyy-MM-dd HH:mm")
    size    = (Get-Item "releases\$bin").Length
    sha256  = $sha
}
[IO.File]::WriteAllText("$PSScriptRoot\releases\manifest.json", ($manifest | ConvertTo-Json))

Write-Host "== Day len GitHub ==" -ForegroundColor Cyan
git add CMakeLists.txt releases
git commit -q -m "pump-control: firmware $Version - $Notes"
git push -q
if ($LASTEXITCODE -ne 0) { Write-Host "PUSH LOI - kiem mang / dang nhap git" -ForegroundColor Red; exit 1 }
Write-Host "XONG: $Version da dang. Khach mo app -> o 'Ban moi' hien $Version (toi da 6 gio, hoac khoi dong lai thiet bi) -> bam 'Cap nhat'." -ForegroundColor Green
