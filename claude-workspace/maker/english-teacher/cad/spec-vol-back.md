# spec-vol-back – đưa 2 nút âm lượng về LƯNG (Tuan 2026-11-08)

cwd: `maker/english-teacher/cad`
allow: `build_owl.py`, `out/**`, `README.md`, `../print/print.yaml`, `../print/stl/**`, `../print/plates/**`, `../print/backup/**`, `backup/**`
**Không sửa:** `gate_owl.py` (Claude đã thêm kiểm nút ở lưng), `export_cad.py`, `community/`, fit-library.
Có thay đổi chưa commit cần GIỮ: `cad/out/*` (bản in cũ – chuyển bản cũ vào `backup/20261108-vol-hai-ben-dau/` trước khi ghi đè), `print/backup/`.

gate (chạy trong cwd, phải exit 0):
```
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl.py -- out
python ..\..\..\tools\robotics-cad\scripts\printability.py out
python ..\..\..\tools\robotics-cad\scripts\slice.py ..\print\print.yaml      (sau khi chép STL mới sang print/stl)
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl.py -- out
python export_cad.py out
```

## Bối cảnh
- Commit 25accf3 tự ý dời vol+/vol− từ lưng lên hai bên đầu (trên đường ráp, z 117, trục x). Tuan: **đưa về lưng**.
- Lý do bản trước bỏ lưng (README mục MX): vỏ sau in **mặt ráp xuống** nên vách lưng thành **trần** của bản in; khối giữ switch treo dưới
  trần cần support. Thêm nữa: switch MX có đầu trên 15,6 nên không lùa qua lỗ ép 14,00 từ phía trong, và vành nắp cũ Ø14,4 không lọt lỗ 14,00.
- Hệ trục: mm, +Z lên, mặt trước −Y, mặt ráp y = 0,37 (`split_plane_y`). Nửa sau = y > 0,37. Mọi số đặt ở đầu `build_owl.py`, ghi `out/owl-params.json`.
- Số MX lấy từ fit-library qua `mx_cutters()` có sẵn (catpaw/mx-socket 14,00 press, sâu 8,58, rãnh V; catpaw/mx-keycap-cross 4,19 × 1,25).

## Thiết kế đã chốt (Claude) – cụm nút rời "vol-pod"
1. **vol-pod** = chi tiết mới `out/vol-pod.stl` (in riêng, màu như vỏ sau "mơ"), mang 2 switch MX + 2 nắp:
   - 2 ổ switch theo đúng kiểu nút nói trên đầu (dùng lại `mx_cutters()` + yên côn 45° + lỗ cổ nắp) với **miệng ổ quay vào TRONG vỏ** (−y), nắp nhô ra **ngoài lưng** (+y).
     Lắp trên bàn: nắp luồn từ phía trong qua ổ 14,00 → tì yên côn; rồi ấn switch vào ổ 14,00 (press). Chân switch quay vào trong để hàn dây.
   - Tâm 2 nút: **x = ±16** (cách nhau 32), cùng z. vol_up ở +x (KEY5 GPIO18), vol_down ở −x (KEY6 GPIO5) – như bản cũ.
   - **z**: chọn trong 85–115 sao cho vách lưng ở đó gần thẳng đứng (pháp tuyến lệch +y ≤ 25°), không đè 5 khe 2 × 18, chốt định vị, khe cáp chân lưng.
     Ghi z đã chọn + lý do vào README.
   - Nắp `mx-cap-vol-up/-down`: giữ đầu Ø17,2 + dấu +/− lõm, cổ Ø8 qua lỗ Ø9,0; **vành Ø13,6** (flange_r 6,8 → hơn lỗ 2,3/bên ≥ 1,5; < 14,00 để luồn qua ổ).
   - Pod có **vành bao** lớn hơn ô cửa ở lưng **≥ 3 mm mỗi phía**, áp vào mặt trong vách lưng → từ ngoài không rút ra được.
     Mặt pod áp vách: bám theo cong vách (khe 0,3) hoặc vách được làm phẳng cục bộ ở mặt trong quanh cửa – chọn cách không tạo phần treo trên bản in vỏ sau.
   - Giữ pod: **2 vít M3** xuyên vành pod (lỗ 3,4) vào **2 đai ốc M3 lục giác** (5,8, hốc sâu 2,8) – số trong bảng khe `spec-owl.md`. Hốc đai ốc/trụ vít trên vỏ sau
     phải in được không support: mặt dưới trụ (theo hướng in) vát ≥ 45° hoặc trụ mọc từ mặt ráp. Nếu không đặt được đai ốc ở vỏ, cho đai ốc nằm ở pod và vít bắt từ ngoài lưng (đầu vít chìm).
   - Pod in **mặt ngoài xuống bàn**, không support (vành, yên côn 45°…).
2. **Ô cửa ở lưng** vỏ sau: chữ nhật bo góc vừa thân pod (khe 0,3/bên), nắp nhô ra ngoài ≤ 4 mm. Xóa đệm bên đầu + lỗ nút hai bên đầu của bản 25accf3,
   trả hai bên đầu về như trước 25accf3 (chốt định vị: giữ chỗ hiện tại nếu không vướng).
3. `owl-params.json` mục `mx.keys`: vol_up/vol_down `axis: "y"`, `pos` = tâm lỗ nắp trên mặt ngoài lưng (y ≥ split + 30), `flange_r: 6.8`, `hole_r: 4.5`,
   `flange_over`; thêm mục `vol_pod` {window, flange_margin, screws}.
4. Lắp ráp `out/asm/`: vol-pod + switch giả + nắp ở đúng vị trí; `owl-assembly.sc` qua `export_cad.py` (mỗi chi tiết 1 component).
5. Bàn in: thêm `vol-pod*.stl` vào `print.yaml` (bàn màu mơ cùng vỏ sau nếu vừa, không thì bàn mới), chép STL mới sang `print/stl/`, cắt lớp **PASS hết bàn, không support**
   (`print-report.json`), bản cũ vào `print/backup/20261108-vol-hai-ben-dau/`.
6. Ảnh duyệt: `out/owl-preview.png`, `out/owl-exploded.png` + **ảnh mới `out/owl-back.png`** nhìn thẳng từ lưng thấy 2 nút + `out/vol-pod.png` (pod + switch + nắp, tách lớp).
7. README: mục nút MX cập nhật (vị trí lưng, cách lắp pod: nắp → switch → hàn dây song song KEY5/KEY6 trên bo → đặt pod từ trong → 2 vít), bảng chi tiết thêm vol-pod.
   An toàn khi hàn: rút USB, mỏ hàn nóng, điện 3,3 V.

## Không làm
- Không đổi nút nói (talk) trên đầu, loa, mắt, bo, dáng ngoài.
- Không đổi số MX trong fit-library, không tự chọn thông số khác ngoài các số ở trên (cần số mới → ghi TODO + báo).
- Không commit (phiên chính commit).

## Tiêu chí PASS
- Chuỗi gate exit 0 (gate_owl có kiểm nút ở lưng, vành ≤ 13,8, cách nhau ≥ 25, mọi bàn PASS).
- Claude tự xem ảnh `owl-back.png`, `vol-pod.png` trước khi đưa Tuan duyệt.
