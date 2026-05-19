# Run this once as Administrator to register the scheduled tasks.
# The newsletter script runs at 8:00 AM KST daily.
# KST = UTC+9, so 8:00 AM KST = 23:00 UTC previous day.
# On a Korean-locale Windows machine set to KST, just use 08:00.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pythonExe = (Get-Command python).Source
$mainScript = Join-Path $scriptDir "main.py"
$logDir = Join-Path $scriptDir "logs"

# Create logs directory
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Task: scrape + generate + send (all in one script, runs at 8:00 AM KST)
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "`"$mainScript`"" `
    -WorkingDirectory $scriptDir

$trigger = New-ScheduledTaskTrigger -Daily -At "08:00AM"

$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -StartWhenAvailable

Register-ScheduledTask `
    -TaskName "AI_Newsletter_Daily" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Scrapes AI & design news, generates newsletter via Claude, sends to Slack at 8:00 AM KST" `
    -RunLevel Highest `
    -Force

Write-Host "Scheduled task 'AI_Newsletter_Daily' registered for 8:00 AM daily." -ForegroundColor Green
Write-Host "Make sure your .env file is configured before the first run." -ForegroundColor Yellow
