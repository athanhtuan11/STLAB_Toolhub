# Tai mo hinh nhan dien giong (speaker embedding, CPU) vao server\models\. Chay lai duoc.
# Thu vien: sherpa-onnx (Apache-2.0), cai vao runtime\.venv.
# Mo hinh: 3D-Speaker CAM++ zh_en 16k advanced, tu trang release k2-fsa/sherpa-onnx "speaker-recongition-models".
# License trong so: 3D-Speaker (alibaba-damo-academy) cong bo Apache-2.0; trang release khong ghi rieng
#   -> TODO: xac minh lai tren the mo hinh ModelScope neu dung thuong mai.
# Trang release khong cong bo sha256: script ghi sha256 lan tai dau vao models\voiceid.sha256 va kiem o cac lan sau.
$ErrorActionPreference = "Stop"
$H = $PSScriptRoot
$uv = "C:\Users\hoang\.local\bin\uv.exe"
if (-not (Test-Path $uv)) { $uv = (Get-Command uv -ErrorAction Stop).Source }
& $uv pip install --python (Join-Path $H "runtime\.venv\Scripts\python.exe") sherpa-onnx numpy
if ($LASTEXITCODE -ne 0) { throw "cai sherpa-onnx loi" }
$M = Join-Path $H "models"
New-Item -ItemType Directory -Force $M | Out-Null
$name = "3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx"
$dst = Join-Path $M $name
$url = "https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/$name"
$shaFile = Join-Path $M "voiceid.sha256"
if (-not (Test-Path $dst)) {
  Invoke-WebRequest -Uri $url -OutFile "$dst.part" -UseBasicParsing
  Move-Item "$dst.part" $dst -Force
}
$h = (Get-FileHash $dst -Algorithm SHA256).Hash.ToLower()
if (Test-Path $shaFile) {
  $old = (Get-Content $shaFile -Raw).Trim()
  if ($old -ne $h) { Remove-Item $dst; throw "sha256 khong khop ($h != $old), da xoa file, chay lai" }
} else { Set-Content -Path $shaFile -Value $h -Encoding ascii }
Write-Host "OK $name sha256=$h"
