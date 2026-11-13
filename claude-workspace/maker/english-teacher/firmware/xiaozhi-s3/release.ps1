# Phat hanh firmware S3 cho may chu lab (OTA qua Wi-Fi). 2026-11-13
#   powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Bump
#   powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Version 2.5.2.1
# Lam: ghi VERSION -> sync.ps1 -> build.ps1 -> check_s3.py -> doc version trong xiaozhi.bin ->
# chep vao server\data\firmware\s3\xiaozhi-<ver>.bin + manifest.json (giu toi da 3 ban, ban cu hon -> server\backup\<ngay>-firmware-cu\).
# KHONG nap vao bo, KHONG khoi dong lai may chu: bo tu cap nhat o lan khoi dong sau.
param(
    [string]$Version = "",
    [switch]$Bump
)
$ErrorActionPreference = 'Stop'
$H = $PSScriptRoot
$verFile = Join-Path $H 'VERSION'
$cur = (Get-Content $verFile -Raw).Trim()

if ($Bump) {
    $p = $cur.Split('.')
    $p[-1] = [string]([int]$p[-1] + 1)
    $Version = $p -join '.'
}
if (-not $Version) { Write-Host 'Can -Bump hoac -Version x.y.z[.w]' -ForegroundColor Red; exit 1 }
if ($Version -notmatch '^\d+(\.\d+){2,3}$') { Write-Host "Phien ban phai dang x.y.z hoac x.y.z.w: $Version" -ForegroundColor Red; exit 1 }

$FW = Join-Path $H '..\..\server\data\firmware\s3'
New-Item -ItemType Directory -Force $FW | Out-Null
$FW = (Resolve-Path $FW).Path
# khong cho phat hanh ban khong moi hon ban da phat hanh (bo se khong cap nhat)
$mf = Join-Path $FW 'manifest.json'
if (Test-Path $mf) {
    $old = (Get-Content $mf -Raw | ConvertFrom-Json).version
    $po = @($old.Split('.') | ForEach-Object { [int]$_ }); $pn = @($Version.Split('.') | ForEach-Object { [int]$_ })
    $newer = $false; $decided = $false
    for ($i = 0; $i -lt [Math]::Min($po.Count, $pn.Count); $i++) {
        if ($pn[$i] -gt $po[$i]) { $newer = $true; $decided = $true; break }
        if ($pn[$i] -lt $po[$i]) { $decided = $true; break }
    }
    if (-not $decided -and $pn.Count -gt $po.Count) { $newer = $true }
    if (-not $newer -and $Version -ne $old) { Write-Host "Ban $Version khong moi hon ban da phat hanh $old" -ForegroundColor Red; exit 1 }
}

Set-Content -Path $verFile -Value $Version -Encoding ascii
Write-Host "== sync $Version ==" -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $H 'sync.ps1')
if ($LASTEXITCODE -ne 0) { Set-Content $verFile $cur -Encoding ascii; Write-Host 'sync loi' -ForegroundColor Red; exit 1 }
Write-Host "== build ==" -ForegroundColor Cyan
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $H 'build.ps1')
if ($LASTEXITCODE -ne 0) { Set-Content $verFile $cur -Encoding ascii; Write-Host 'BUILD LOI - xem build.log (tail -30)' -ForegroundColor Red; exit 1 }
Write-Host "== check_s3 ==" -ForegroundColor Cyan
python (Join-Path $H 'check_s3.py')
if ($LASTEXITCODE -ne 0) { Write-Host 'check_s3 FAIL' -ForegroundColor Red; exit 1 }

# doc version trong esp_app_desc_t: anh = header 24 B + segment header 8 B -> struct o 32; version[32] o +16 => offset 48
$bin = 'C:\xzb\s3\build\xiaozhi.bin'
$bytes = [IO.File]::ReadAllBytes($bin)
$magic = [BitConverter]::ToUInt32($bytes, 32)
if ($magic -ne [uint32]::Parse('ABCD5432', 'HexNumber')) { Write-Host ("Khong thay esp_app_desc (magic 0x{0:X8})" -f $magic) -ForegroundColor Red; exit 1 }
$n = 0; while ($bytes[48 + $n] -ne 0 -and $n -lt 32) { $n++ }
$binVer = [Text.Encoding]::ASCII.GetString($bytes, 48, $n)
if ($binVer -ne $Version) { Write-Host "Version trong bin '$binVer' != $Version" -ForegroundColor Red; exit 1 }

$name = "xiaozhi-$Version.bin"
Copy-Item $bin (Join-Path $FW $name) -Force
$sha = (Get-FileHash (Join-Path $FW $name) -Algorithm SHA256).Hash.ToLower()
$m = [ordered]@{
    version  = $Version
    file     = $name
    sha256   = $sha
    size     = (Get-Item (Join-Path $FW $name)).Length
    built_at = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')
}
[IO.File]::WriteAllText($mf, ($m | ConvertTo-Json), (New-Object Text.UTF8Encoding($false)))

# giu 3 ban moi nhat; cu hon -> server\backup\<ngay>-firmware-cu\
$all = Get-ChildItem $FW -Filter 'xiaozhi-*.bin' | Sort-Object LastWriteTime -Descending
if ($all.Count -gt 3) {
    $bk = Join-Path $H ('..\..\server\backup\' + (Get-Date -Format 'yyyyMMdd') + '-firmware-cu')
    New-Item -ItemType Directory -Force $bk | Out-Null
    $all | Select-Object -Skip 3 | ForEach-Object { Move-Item $_.FullName $bk -Force }
}
Write-Host "XONG: $name  sha256=$($sha.Substring(0,12))...  version trong bin = $binVer. May chu tu phat khi bo khoi dong lai (khong can restart may chu)." -ForegroundColor Green
