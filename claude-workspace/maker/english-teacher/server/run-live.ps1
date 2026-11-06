# Chay cau noi xiaozhi <-> Gemini Live. CHI NGUOI LON THU NOI BO. Dung: .\run-live.ps1 [-WsPort 8000] [-HttpPort 8003]  (Ctrl+C de tat)
param([int]$WsPort = 8000, [int]$HttpPort = 8003)
$ErrorActionPreference = "Stop"
try { (Get-Process -Id $PID).PriorityClass = "Normal" } catch {}
$H = $PSScriptRoot
$RT = Join-Path $H "runtime"
$py = Join-Path $RT ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Chua cai: chay .\setup.ps1 truoc" }
if (-not $env:GOOGLE_API_KEY) { throw "Thieu bien moi truong GOOGLE_API_KEY" }
$ip = $env:STLAB_XIAOZHI_SERVER
if (-not $ip) {
  $ip = (Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp, Manual -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -match "^172\.(1[6-9]|2\d|3[01])\." } |
    Select-Object -First 1).IPAddress
}
if (-not $ip) { throw "Khong tim thay IP LAN, dat STLAB_XIAOZHI_SERVER" }
$env:STLAB_XIAOZHI_SERVER = $ip
$env:STLAB_LIVE_WS_PORT = "$WsPort"
$env:STLAB_LIVE_HTTP_PORT = "$HttpPort"
$env:PATH = "$RT;$env:PATH"
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
Write-Host "GEMINI LIVE - CHI NGUOI LON THU NOI BO, KHONG CHO BE DUNG (dieu khoan Gemini API)"
Write-Host "Cau noi: ws://${ip}:${WsPort}/xiaozhi/v1/  OTA: http://${ip}:${HttpPort}/xiaozhi/ota/"
$ErrorActionPreference = "Continue"
& $py (Join-Path $H "live\bridge.py") 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath (Join-Path $RT "live.log")
