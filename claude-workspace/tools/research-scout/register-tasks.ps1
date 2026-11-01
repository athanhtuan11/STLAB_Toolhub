param([switch]$Unregister)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Scan = Join-Path $Here 'scan.py'
$Digest = Join-Path $Here 'digest.py'
if ($Unregister) {
  Unregister-ScheduledTask -TaskName 'STLab-Research-Scan' -Confirm:$false -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName 'STLab-Research-Digest' -Confirm:$false -ErrorAction SilentlyContinue
  exit 0
}
$Python = (Get-Command python).Source
$scanAction = New-ScheduledTaskAction -Execute $Python -Argument ('"' + $Scan + '"') -WorkingDirectory $Here
$digestAction = New-ScheduledTaskAction -Execute $Python -Argument ('"' + $Digest + '"') -WorkingDirectory $Here
Register-ScheduledTask -TaskName 'STLab-Research-Scan' -Action $scanAction -Trigger (New-ScheduledTaskTrigger -Daily -At 7:00AM) -Settings (New-ScheduledTaskSettingsSet -StartWhenAvailable) -Description 'STLab public research scan' -Force | Out-Null
Register-ScheduledTask -TaskName 'STLab-Research-Digest' -Action $digestAction -Trigger (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 7:30AM) -Settings (New-ScheduledTaskSettingsSet -StartWhenAvailable) -Description 'STLab weekly research digest' -Force | Out-Null
