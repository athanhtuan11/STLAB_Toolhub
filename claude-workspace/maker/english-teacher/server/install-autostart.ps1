# Bat may chu xiaozhi STLab (run.ps1, an cua so) moi khi user hien tai dang nhap Windows. Chay lai duoc.
# Go:  .\install-autostart.ps1 -Remove     (hoac Unregister-ScheduledTask -TaskName "STLab xiaozhi server")
# Log: runtime\server.log, runtime\whisper.log
param([switch]$Remove)
$ErrorActionPreference = "Stop"
$name = "STLab xiaozhi server"
if ($Remove) {
  Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host "Da go tac vu '$name'"
  return
}
$run = Join-Path $PSScriptRoot "run.ps1"
$user = "$env:USERDOMAIN\$env:USERNAME"
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$run`"" -WorkingDirectory $PSScriptRoot
# Tre 60 s sau dang nhap cho mang co IP (run-live.ps1 con tu cho them toi 3 phut)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$trigger.Delay = "PT60S"
# 2026-11-08: lan dang nhap 18:42 task thoat 0xC000013A -> Windows tu chay lai khi loi (moi 1 phut, toi 999 lan)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -Priority 4 `
  -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "Da dang ky '$name': chay $run luc dang nhap (tre 30 s)"
