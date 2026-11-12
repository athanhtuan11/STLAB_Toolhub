# Chep ban ghim xiaozhi-esp32 (chi doc) sang build-src/, them bo stlab-s3, ap patch, ghi sdkconfig.defaults.
# build-src la JUNCTION ngan -> C:\xzb\s3: Python/CMake giai junction/subst ve duong that, ma duong dan dai
# (D:\04_Stlab\...\xiaozhi-s3\build-src) lam dong lenh bien dich vuot 32767 ky tu -> thu muc THAT phai ngan.
$ErrorActionPreference = 'Stop'
$H = $PSScriptRoot
$WS = (Resolve-Path (Join-Path $H '..\..\..\..')).Path
$Src = Join-Path $WS 'community\78-xiaozhi-esp32'
$Dst = Join-Path $H 'build-src'
$Real = 'C:\xzb\s3'

$head = (git -C $Src rev-parse HEAD).Trim()
if (-not $head.StartsWith('49b4380')) { throw "Ban ghim sai: $head (can 49b4380...)" }

# May chu trong lab: bien STLAB_XIAOZHI_SERVER, khong co thi lay IPv4 LAN cua may nay
$ip = $env:STLAB_XIAOZHI_SERVER
if ([string]::IsNullOrWhiteSpace($ip)) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -match '^(192\.168|10\.|172\.(1[6-9]|2\d|3[01]))\.' -and $_.InterfaceAlias -notmatch 'vEthernet|WSL|Loopback|VMware|VirtualBox' } |
        Select-Object -First 1).IPAddress
    if (-not $ip) { throw 'Khong tim thay IPv4 LAN; dat $env:STLAB_XIAOZHI_SERVER' }
    Write-Warning "STLAB_XIAOZHI_SERVER chua dat -> dung IP LAN may nay: $ip"
}
$ota = "http://${ip}:8003/xiaozhi/ota/"

# thu muc that ngan; giu managed_components (tai tu mang, ghim theo manifest) de khong tai lai moi lan
New-Item -ItemType Directory -Path $Real -Force | Out-Null
$cache = 'C:\xzb\mc-cache-s3'
if (Test-Path $cache) { Remove-Item -Recurse -Force $cache }
if (Test-Path (Join-Path $Real 'managed_components')) { Move-Item (Join-Path $Real 'managed_components') $cache }
Get-ChildItem $Real -Force | Remove-Item -Recurse -Force

# build-src: neu dang la thu muc that (ban cu) thi bo; roi tao junction
$item = Get-Item $Dst -Force -ErrorAction SilentlyContinue
if ($item -and -not $item.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) { Remove-Item -Recurse -Force $Dst }
if (-not (Test-Path $Dst)) { cmd /c mklink /J "$Dst" "$Real" | Out-Null }
if (-not (Test-Path $Dst)) { throw 'Khong tao duoc junction build-src' }

# robocopy: chep het tru .git; ma tra ve < 8 la thanh cong
robocopy $Src $Real /E /XD .git /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy loi $LASTEXITCODE" }
if (Test-Path $cache) { Move-Item $cache (Join-Path $Real 'managed_components') }

$boardDst = Join-Path $Real 'main\boards\stlab-s3'
New-Item -ItemType Directory -Path $boardDst -Force | Out-Null
Copy-Item (Join-Path $H 'boards\stlab-s3\*') $boardDst -Recurse -Force

# git apply chay trong C:\xzb\s3 (ngoai moi repo) de duong dan patch tinh tu goc thu muc nay
Push-Location $Real
try {
    foreach ($p in (Get-ChildItem (Join-Path $H 'patches') -Filter *.patch | Sort-Object Name)) {
        git apply --ignore-whitespace --whitespace=nowarn $p.FullName
        if ($LASTEXITCODE -ne 0) { throw "git apply loi: $($p.Name)" }
    }
    if (-not (Select-String -Path 'main\Kconfig.projbuild' -Pattern 'BOARD_TYPE_STLAB_S3' -Quiet)) { throw 'Patch Kconfig khong ap' }
    if (-not (Select-String -Path 'main\CMakeLists.txt' -Pattern 'stlab-s3' -Quiet)) { throw 'Patch CMake khong ap' }
    if (-not (Select-String -Path 'main\audio\engines\afe_audio_engine.cc' -Pattern 'stlab_afe_out_hook' -Quiet)) { throw 'Patch AFE hook khong ap' }
} finally { Pop-Location }

# sdkconfig.defaults: dong cuoi thang (Kconfig choice lay gia tri cuoi); xoa sdkconfig cu de sinh lai
$extra = (Get-Content (Join-Path $H 'sdkconfig.stlab') -Raw).Replace('@OTA_URL@', $ota)
Add-Content -Path (Join-Path $Real 'sdkconfig.defaults') -Value "`n$extra" -Encoding ascii
# sdkconfig.defaults.esp32s3 nap SAU sdkconfig.defaults va ghi de (vd LV_USE_BUILTIN_MALLOC) -> them ca vao do de STLab thang
Add-Content -Path (Join-Path $Real 'sdkconfig.defaults.esp32s3') -Value "`n$extra" -Encoding ascii
Remove-Item -Force (Join-Path $Real 'sdkconfig') -ErrorAction SilentlyContinue
Write-Host "sync OK  ban ghim $($head.Substring(0,7))  OTA_URL=$ota  build-src -> $Real"
