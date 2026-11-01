param(
    [switch]$Unregister,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspace = (Resolve-Path (Join-Path $scriptDir '..\..')).Path
$taskNames = @('STLab-Backup-FCStd', 'STLab-Community-Check')
if ($Unregister) {
    foreach ($name in $taskNames) {
        Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
        Write-Output $name
    }
    return
}
$python = (Get-Command python -ErrorAction Stop).Source
$bash = 'C:\Program Files\Git\bin\bash.exe'
$definitions = @(
    @{ Name = 'STLab-Backup-FCStd'; Program = $python; Arguments = 'backup_fcstd.py'; Working = $scriptDir; Day = $null; Time = '21:00' },
    @{ Name = 'STLab-Community-Check'; Program = $bash; Arguments = 'community/update-community.sh check'; Working = $workspace; Day = 'Sunday'; Time = '09:00' }
)
foreach ($item in $definitions) {
    $action = New-ScheduledTaskAction -Execute $item.Program -Argument $item.Arguments -WorkingDirectory $item.Working
    if ($null -eq $item.Day) {
        $trigger = New-ScheduledTaskTrigger -Daily -At $item.Time
    } else {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $item.Day -At $item.Time
    }
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable
    Register-ScheduledTask -TaskName $item.Name -Action $action -Trigger $trigger -Settings $settings -User $env:USERNAME -Force | Out-Null
    $next = (Get-ScheduledTaskInfo -TaskName $item.Name).NextRunTime
    Write-Output ("{0} {1}" -f $item.Name, $next)
}
