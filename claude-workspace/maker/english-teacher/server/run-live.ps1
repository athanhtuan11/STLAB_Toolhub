# Chay cau noi xiaozhi <-> Gemini Live. CHI NGUOI LON THU NOI BO. Dung: .\run-live.ps1 [-WsPort 8000] [-HttpPort 8003]  (Ctrl+C de tat)
param([int]$WsPort = 8000, [int]$HttpPort = 8003)
$ErrorActionPreference = "Stop"
try { (Get-Process -Id $PID).PriorityClass = "Normal" } catch {}
$H = $PSScriptRoot
$RT = Join-Path $H "runtime"
$py = Join-Path $RT ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Chua cai: chay .\setup.ps1 truoc" }
if (-not $env:GOOGLE_API_KEY) { throw "Thieu bien moi truong GOOGLE_API_KEY" }
$LOG = Join-Path $RT "live.log"
function Note($m) { $l = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [RUN-LIVE] $m"; Write-Host $l; Add-Content -Path $LOG -Value $l -Encoding utf8 }
# 2026-11-08: luc vua dang nhap mang co the chua co IP -> cho toi da 3 phut thay vi thoat ngay
$ip = $env:STLAB_XIAOZHI_SERVER
for ($k = 0; -not $ip -and $k -lt 36; $k++) {
  $ip = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp, Manual -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -match "^172\.(1[6-9]|2\d|3[01])\." } |
    Select-Object -First 1).IPAddress
  if (-not $ip) { Start-Sleep 5 }
}
if (-not $ip) { Note "Khong tim thay IP LAN sau 3 phut, dat STLAB_XIAOZHI_SERVER"; throw "Khong tim thay IP LAN" }
$env:STLAB_XIAOZHI_SERVER = $ip
$env:STLAB_LIVE_WS_PORT = "$WsPort"
$env:STLAB_LIVE_HTTP_PORT = "$HttpPort"
$env:PATH = "$RT;$env:PATH"
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
Write-Host "GEMINI LIVE - CHI NGUOI LON THU NOI BO, KHONG CHO BE DUNG (dieu khoan Gemini API)"
Write-Host "Cau noi: ws://${ip}:${WsPort}/xiaozhi/v1/  OTA: http://${ip}:${HttpPort}/xiaozhi/ota/"
$ErrorActionPreference = "Continue"
# 2026-11-11: truy cap tu internet qua VPS (deploy/README.md). Co FRP_SERVER_ADDR thi bat frpc an (tu noi lai khi mat mang).
$frpc = Join-Path $H "deploy\bin\frpc.exe"
function Start-Frpc {
  if (-not $env:FRP_SERVER_ADDR) { return }
  if (-not (Test-Path $frpc)) { Note "co FRP_SERVER_ADDR nhung chua co deploy\bin\frpc.exe (chay deploy\get-frpc.ps1)"; return }
  if (Get-Process frpc -ErrorAction SilentlyContinue) { return }
  Start-Process $frpc -ArgumentList "-c", (Join-Path $H "deploy\frpc.toml") -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $RT "frpc.log") -RedirectStandardError (Join-Path $RT "frpc.err.log")
  Note "bat frpc -> $($env:FRP_SERVER_ADDR):7000 (domain $($env:STLAB_PUBLIC_HOST))"
}
# 2026-11-08: task luc dang nhap tung thoat 0xC000013A ma log bi ghi de -> ghi NOI log + bridge thoat thi tu chay lai sau 10 s
# (Ctrl+C khi chay tay van tat ca script). Log qua 5 MB thi doi ten thanh live.old.log.
while ($true) {
  if ((Test-Path $LOG) -and (Get-Item $LOG).Length -gt 5MB) { Move-Item $LOG (Join-Path $RT "live.old.log") -Force }
  Start-Frpc
  Note "khoi dong bridge (ip $ip, pid $PID)"
  & $py (Join-Path $H "live\bridge.py") 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $LOG -Append
  Note "bridge thoat, ma $LASTEXITCODE - chay lai sau 10 s"
  Start-Sleep 10
}
