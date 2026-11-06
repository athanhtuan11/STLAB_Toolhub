# Chay may chu xiaozhi STLab. Dung: .\run.ps1  (Ctrl+C de tat). IP: bien STLAB_XIAOZHI_SERVER hoac IPv4 LAN tu dong.
$ErrorActionPreference = "Stop"
# Task Scheduler chay o muc BelowNormal -> Whisper cham 2 s -> 6 s (do 2026-11-06). Nang len Normal; tien trinh con ke thua.
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

# sinh runtime/data/.config.yaml (khong chua khoa)
$prompt = ((Get-Content (Join-Path $H "prompt-teacher.md") -Raw -Encoding utf8) -split "(?m)^-----\s*$", 2)[1].Trim() -split "\r?\n"
$promptYaml = ($prompt | ForEach-Object { if ($_ -eq "") { "" } else { "  " + $_ } }) -join "`n"
$cfg = Get-Content (Join-Path $H "stlab.config.yaml") -Raw -Encoding utf8
$cfg = $cfg.Replace("<IP>", $ip).Replace("  <PROMPT>", $promptYaml)
New-Item -ItemType Directory -Force (Join-Path $RT "data") | Out-Null
[IO.File]::WriteAllText((Join-Path $RT "data\.config.yaml"), $cfg, (New-Object Text.UTF8Encoding $false))
Copy-Item (Join-Path $H "stlab-base-prompt.txt") (Join-Path $RT "stlab-base-prompt.txt") -Force

Write-Host "May chu xiaozhi: ws://${ip}:8000/xiaozhi/v1/  OTA: http://${ip}:8003/xiaozhi/ota/"
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
$ffdir = Split-Path (Get-Command ffmpeg -ErrorAction Stop).Source
$ErrorActionPreference = "Continue"
# Whisper tai may (127.0.0.1:8010) bat truoc, cho san sang roi moi bat server; tat server thi tat ca Whisper
$wpy = Join-Path $H "whisper-local\.venv\Scripts\python.exe"
if (-not (Test-Path $wpy)) { throw "Chua cai Whisper: chay .\setup.ps1 truoc" }
if (-not $env:STLAB_WHISPER_MODEL) { $env:STLAB_WHISPER_MODEL = "small" }
$wlog = Join-Path $RT "whisper.log"
$wp = Start-Process -FilePath $wpy -ArgumentList (Join-Path $H "whisper-local\server.py") -WorkingDirectory $H -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput $wlog -RedirectStandardError (Join-Path $RT "whisper.err.log")
try {
  $ready = $false
  for ($i = 0; $i -lt 120; $i++) {
    try { if ((Invoke-WebRequest "http://127.0.0.1:8010/health" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200) { $ready = $true; break } } catch {}
    if ($wp.HasExited) { throw "Whisper tat bat ngo, xem $wlog" }
    Start-Sleep -Seconds 1
  }
  if (-not $ready) { throw "Whisper khong san sang sau 120 s" }
  Write-Host "Whisper san sang (model $env:STLAB_WHISPER_MODEL) tai 127.0.0.1:8010"
  & $py (Join-Path $H "run.py") 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath (Join-Path $RT "server.log")
} finally {
  if ($wp -and -not $wp.HasExited) { Stop-Process -Id $wp.Id -Force -ErrorAction SilentlyContinue }
}
