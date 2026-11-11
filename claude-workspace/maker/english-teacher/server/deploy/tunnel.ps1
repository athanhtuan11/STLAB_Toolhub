# Duong ham SSH may lab -> VPS (OpenSSH co san trong Windows; frpc bi Defender chan 2026-11-11).
# VPS mo 127.0.0.1:18003 -> lab 8003 (OTA), 127.0.0.1:18000 -> lab 8000 (WebSocket); nginx tren VPS chuyen tiep vao.
# User engtunnel tren VPS: khong shell, chi duoc mo dung 2 cong nay (authorized_keys permitlisten).
# Bien: STLAB_TUNNEL_HOST (vd engtunnel@180.93.138.55). Khoa: %USERPROFILE%\.ssh\id_ed25519_engtunnel. Rot thi tu noi lai sau 5 s.
$ErrorActionPreference = "Continue"
$target = $env:STLAB_TUNNEL_HOST
if (-not $target) { Write-Host "Thieu STLAB_TUNNEL_HOST"; exit 1 }
$ssh = Join-Path $env:SystemRoot "System32\OpenSSH\ssh.exe"
$key = Join-Path $env:USERPROFILE ".ssh\id_ed25519_engtunnel"
$log = Join-Path $PSScriptRoot "..\runtime\tunnel.log"
function Note($m) { Add-Content -Path $log -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [TUNNEL] $m" -Encoding utf8 }
while ($true) {
  Note "noi $target"
  & $ssh -N -i $key -o BatchMode=yes -o StrictHostKeyChecking=yes -o ExitOnForwardFailure=yes `
    -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o ConnectTimeout=15 `
    -R 127.0.0.1:18003:127.0.0.1:8003 -R 127.0.0.1:18000:127.0.0.1:8000 $target 2>&1 |
    ForEach-Object { Note "$_" }
  Note "rot (ma $LASTEXITCODE) - noi lai sau 5 s"
  Start-Sleep 5
}
