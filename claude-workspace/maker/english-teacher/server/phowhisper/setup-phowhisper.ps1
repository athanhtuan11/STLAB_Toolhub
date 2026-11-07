# Cai PhoWhisper (VinAI, BSD-3-Clause) -> CTranslate2 int8 cho faster-whisper. Chay lai duoc (bo qua model da co).
# Dung: .\setup-phowhisper.ps1 [-Sizes small,medium]
param([string[]]$Sizes = @("small", "medium"))
$ErrorActionPreference = "Stop"
$H = $PSScriptRoot
$MODELS = (Resolve-Path (Join-Path $H "..")).Path + "\models"
$uv = "C:\Users\hoang\.local\bin\uv.exe"
if (-not (Test-Path $uv)) { $uv = (Get-Command uv -ErrorAction Stop).Source }
$venv = Join-Path $H ".venv"
$py = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $py)) { & $uv venv $venv --python 3.12; if ($LASTEXITCODE) { throw "uv venv loi" } }
& $uv pip install --python $py --index-url https://download.pytorch.org/whl/cpu torch --extra-index-url https://pypi.org/simple
if ($LASTEXITCODE) { throw "cai torch loi" }
& $uv pip install --python $py transformers ctranslate2 faster-whisper edge-tts huggingface_hub numpy "av<17"
if ($LASTEXITCODE) { throw "cai goi loi" }
New-Item -ItemType Directory -Force $MODELS | Out-Null
$conv = Join-Path $venv "Scripts\ct2-transformers-converter.exe"
foreach ($s in $Sizes) {
  $out = Join-Path $MODELS "phowhisper-$s-ct2"
  if (Test-Path (Join-Path $out "model.bin")) { Write-Host "Da co $out"; continue }
  Write-Host "Chuyen vinai/PhoWhisper-$s -> $out"
  & $conv --model "vinai/PhoWhisper-$s" --output_dir $out --quantization int8 --copy_files tokenizer.json preprocessor_config.json --force
  if ($LASTEXITCODE) { throw "chuyen $s loi" }
}
Get-ChildItem $MODELS -Directory -Filter "phowhisper-*" | ForEach-Object {
  "{0}: {1:N0} MB" -f $_.Name, ((Get-ChildItem $_.FullName -Recurse | Measure-Object Length -Sum).Sum / 1MB)
}
