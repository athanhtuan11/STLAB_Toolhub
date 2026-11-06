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
# Tre 30 s sau dang nhap cho Wi-Fi co IP (run.ps1 lay IPv4 LAN)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $user
$trigger.Delay = "PT30S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -Priority 4
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Write-Host "Da dang ky '$name': chay $run luc dang nhap (tre 30 s)"
