# run-plan.ps1 - chay 1 phien Claude Code khong nguoi trong theo file ke hoach, ghi log, xong thi hen tat may (Tuan 2026-11-27).
#   powershell -ExecutionPolicy Bypass -File tools\auto-run\run-plan.ps1 -Plan docs\plans\auto-run-20261128-cad-perf.md [-Shutdown]
# Tat may: shutdown /s /t 300 (con 5 phut; huy bang "shutdown /a").
param(
    [Parameter(Mandatory = $true)][string]$Plan,
    [switch]$Shutdown
)
$ws = "D:\04_Stlab\04_STLAB_Toolhub\claude-workspace"
Set-Location $ws
$logDir = Join-Path $ws "docs\plans\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir ("auto-run-" + (Get-Date -Format "yyyyMMdd-HHmm") + ".log")

# claude.exe: ban moi nhat trong extension VS Code (duong dan doi theo phien ban), du phong PATH
$exe = Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Directory -Filter "anthropic.claude-code-*" -ErrorAction SilentlyContinue |
    Sort-Object Name -Descending | ForEach-Object { Join-Path $_.FullName "resources\native-binary\claude.exe" } |
    Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) { $exe = (Get-Command claude -ErrorAction SilentlyContinue).Source }
"[$(Get-Date -Format s)] START plan=$Plan exe=$exe" | Out-File $log -Encoding utf8

if ($exe) {
    $prompt = "Thuc hien ke hoach trong file $Plan (doc file do truoc). Phien khong nguoi trong: khong hoi, tu quyet theo ke hoach."
    & $exe -p $prompt --permission-mode acceptEdits `
        --allowedTools "Bash" "PowerShell" "Read" "Edit" "Write" "Glob" "Grep" "Agent" "Skill" "ToolSearch" `
        --output-format text *>> $log
    "[$(Get-Date -Format s)] END exit=$LASTEXITCODE" | Out-File $log -Append -Encoding utf8
} else {
    "[$(Get-Date -Format s)] KHONG TIM THAY claude.exe" | Out-File $log -Append -Encoding utf8
}

if ($Shutdown) {
    "[$(Get-Date -Format s)] shutdown /s /t 300" | Out-File $log -Append -Encoding utf8
    shutdown /s /t 300 /c "STLab auto-run xong - tat may sau 5 phut (huy: shutdown /a)"
}
