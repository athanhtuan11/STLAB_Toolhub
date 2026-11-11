# Tai frpc.exe (Windows) cho may lab, kiem sha256 theo file checksum cua ban phat hanh. Dung:
#   .\deploy\get-frpc.ps1 -Version <x.y.z>   (cung phien ban voi frps tren VPS)
param([Parameter(Mandatory)][string]$Version)
$ErrorActionPreference = "Stop"
$bin = Join-Path $PSScriptRoot "bin"
New-Item -ItemType Directory -Force $bin | Out-Null
$name = "frp_${Version}_windows_amd64"
$base = "https://github.com/fatedier/frp/releases/download/v$Version"
$tmp = Join-Path $env:TEMP "frp-$Version"
New-Item -ItemType Directory -Force $tmp | Out-Null
Invoke-WebRequest "$base/$name.zip" -OutFile "$tmp\$name.zip" -UseBasicParsing
Invoke-WebRequest "$base/frp_sha256_checksums.txt" -OutFile "$tmp\sums.txt" -UseBasicParsing
$want = ((Get-Content "$tmp\sums.txt") | Where-Object { $_ -match " $name\.zip$" }) -split '\s+' | Select-Object -First 1
$got = (Get-FileHash "$tmp\$name.zip" -Algorithm SHA256).Hash.ToLower()
if (-not $want -or $got -ne $want.ToLower()) { throw "Sai sha256 cho $name.zip" }
Expand-Archive "$tmp\$name.zip" -DestinationPath $tmp -Force
Copy-Item "$tmp\$name\frpc.exe" (Join-Path $bin "frpc.exe") -Force
Remove-Item $tmp -Recurse -Force
Write-Host "Da tai frpc $Version -> $bin\frpc.exe (sha256 OK)"
