# Cai may chu xiaozhi (khong Docker). Chay lai duoc. Log: runtime/setup.log
$ErrorActionPreference = "Stop"
$H = $PSScriptRoot
$WS = (Resolve-Path (Join-Path $H "..\..\..")).Path
$SRC = Join-Path $WS "community\xinnan-tech-xiaozhi-esp32-server\main\xiaozhi-server"
$RT = Join-Path $H "runtime"
$uv = "C:\Users\hoang\.local\bin\uv.exe"
if (-not (Test-Path $uv)) { $uv = (Get-Command uv -ErrorAction Stop).Source }
New-Item -ItemType Directory -Force $RT | Out-Null
$log = Join-Path $RT "setup.log"
function Log($m) { $l = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m; Write-Host $l; Add-Content -Path $log -Value $l -Encoding utf8 }
function Run($exe, $argList) {
  Log ("> " + (Split-Path $exe -Leaf) + " " + ($argList -join " "))
  $ErrorActionPreference = "Continue"
  $out = & $exe @argList 2>&1 | ForEach-Object { "$_" }
  $code = $LASTEXITCODE
  $out | Select-Object -Last 15 | ForEach-Object { Add-Content -Path $log -Value $_ -Encoding utf8 }
  if ($code -ne 0) { throw "Lenh loi (exit $code), xem $log" }
}

# 1. chep ma nguon (giu runtime/models, runtime/.venv, runtime/setup.log)
Log "Chep ma nguon xiaozhi-server -> runtime/"
Get-ChildItem $RT -Force | Where-Object { $_.Name -notin @("models", ".venv", "setup.log", "server.log", "opus.dll") } | Remove-Item -Recurse -Force
Get-ChildItem $SRC -Force | Where-Object { $_.Name -ne "models" } | Copy-Item -Destination $RT -Recurse -Force
# models: chep file nho (silero, cau hinh SenseVoice) neu thieu, khong ghi de model.pt
foreach ($f in Get-ChildItem (Join-Path $SRC "models") -Recurse -File) {
  $rel = $f.FullName.Substring((Join-Path $SRC "models").Length).TrimStart("\")
  $dst = Join-Path $RT ("models\" + $rel)
  if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null; Copy-Item $f.FullName $dst }
}
New-Item -ItemType Directory -Force (Join-Path $RT "data") | Out-Null

# 2. venv python 3.10
$py = Join-Path $RT ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Run $uv @("venv", (Join-Path $RT ".venv"), "--python", "3.10") }

# 3. torch CPU roi requirements
$ErrorActionPreference = "Continue"
$null = & $py -c "import torch,funasr" 2>&1
$have = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = "Stop"
if (-not $have) {
  Run $uv @("pip", "install", "--python", $py, "--index-url", "https://download.pytorch.org/whl/cpu", "torch==2.2.2", "torchaudio==2.2.2")
  Run $uv @("pip", "install", "--python", $py, "-r", (Join-Path $RT "requirements.txt"))
} else { Log "torch/funasr da co, bo qua cai dat" }

# 4. model SenseVoiceSmall (modelscope)
$mp = Join-Path $RT "models\SenseVoiceSmall\model.pt"
if (-not (Test-Path $mp) -or (Get-Item $mp).Length -lt 100MB) {
  Run $py @("-c", "from modelscope.hub.file_download import model_file_download as d; import shutil; p=d('iic/SenseVoiceSmall','model.pt'); shutil.copyfile(p, r'$mp'); print(p)")
} else { Log "model.pt da co" }
# 5. opus.dll (opuslib_next tren Windows can; lay ban co san cua FreeCAD, chep vao runtime/)
if (-not (Test-Path (Join-Path $RT "opus.dll"))) {
  $o = Get-ChildItem "C:\Program Files\FreeCAD*in\opus.dll", "C:\Program Files\VCMI\opus.dll" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($o) { Copy-Item $o.FullName (Join-Path $RT "opus.dll"); Log "opus.dll tu $($o.FullName)" } else { Log "CANH BAO: khong thay opus.dll, tu dat opus.dll vao runtime\" }
}
# 6. Whisper tai may (venv rieng, faster-whisper CPU int8) + tai model
$WL = Join-Path $H "whisper-local"
$wpy = Join-Path $WL ".venv\Scripts\python.exe"
if (-not (Test-Path $wpy)) { Run $uv @("venv", (Join-Path $WL ".venv"), "--python", "3.10") }
Run $uv @("pip", "install", "--python", $wpy, "faster-whisper", "fastapi", "uvicorn", "python-multipart")
$wm = if ($env:STLAB_WHISPER_MODEL) { $env:STLAB_WHISPER_MODEL } else { "small" }
Run $wpy @("-c", "from faster_whisper import WhisperModel; WhisperModel('$wm', device='cpu', compute_type='int8'); print('model $wm san sang')")
Log "XONG setup"
