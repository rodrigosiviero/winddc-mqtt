param(
    [string]$TaskName = "WinddcMqtt",
    [switch]$Remove
)

$root = Split-Path -Parent $PSScriptRoot
if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    exit 0
}

$python = Join-Path $root ".venv\Scripts\pythonw.exe"
$entrypoint = Join-Path $root "start.py"
if (!(Test-Path $python) -or !(Test-Path $entrypoint)) {
    throw "Install dependencies first: py -3.12 -m venv .venv; .venv\Scripts\python.exe -m pip install -r requirements.txt"
}

$action = New-ScheduledTaskAction -Execute $python -Argument ('"{0}"' -f $entrypoint) -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "DDC/CI to MQTT bridge in the interactive desktop session" -Force
