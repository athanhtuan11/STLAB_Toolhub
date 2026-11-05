# Chay may chu xiaozhi STLab. Dung: .\run.ps1  (Ctrl+C de tat). IP: bien STLAB_XIAOZHI_SERVER hoac IPv4 LAN tu dong.
$ErrorActionPreference = "Stop"
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

Write-Host "May chu xiaozhi: ws://${ip}:8000/xiaozhi/v1/  OTA: http://${ip}:8003/xiaozhi/ota/"
$env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUTF8 = "1"
$ffdir = Split-Path (Get-Command ffmpeg -ErrorAction Stop).Source
$ErrorActionPreference = "Continue"
& $py (Join-Path $H "run.py") 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath (Join-Path $RT "server.log")
