# Plan chuẩn hóa quy trình CAD → in 3D (STLab)

Viết 2026-10-23, sau đợt làm `pushrod_arm`. Tuan sửa/bổ sung trực tiếp file này.
Trạng thái mỗi mục: `[x]` đã có · `[ ]` chưa làm · `[?]` chờ Tuan quyết.

## 0. Hiện trạng (đã có, đo trên pushrod_arm, 85 chi tiết, 51 STL, 9 bàn in)

| Bước | Lệnh | Thời gian |
|---|---|---|
| Kiểm nhanh (hình học, lưới, va chạm, cache) | `scripts/check.py` | ~40 s lần đầu |
| Xuất STL theo hướng in (hướng in khai trong YAML) | `scripts/export-stl.py` | ~5 s |
| Cắt lớp Bambu CLI, lơ lửng → xoay → support | `scripts/slice.py` | ~20 s |
| **Cả vòng 1 lệnh** | `scripts/prepare-print.py maker/<project>/print/print.yaml` | **~1 phút** (trước: >1 giờ) |

Quy tắc đã chốt: khe lắp ghép 0,2 mm; 1 phiên Claude giữ FreeCAD; sửa model xong tự lưu (có backup);
kiểm ổn thì tự commit + push GitHub. Chi tiết: `maker/robotics-cad/CLAUDE.md`.

## 1. Cộng đồng làm thế nào (tìm 2026-10-23)

- **Slicer là nơi kiểm khả năng in**; CAD lo hình học + lắp ráp. Bambu/Orca CLI xuất 3MF có thời gian, số gam, cảnh báo
  (`result.json`, `slice_info.config`) → STLab đã dùng.
- **"Bot" tự sinh file sản xuất từ dự án** (KiBot cho KiCad, FCBot cho FreeCAD): chạy theo tag/release, đính file
  STEP/STL/3MF + tài liệu vào GitHub Release, có changelog. Chưa có công cụ dựng sẵn cho in 3D → tự ghép.
- **CI trên GitHub Actions**: FreeCAD headless (`freecadcmd`) xuất STEP/STL mỗi lần push/PR; slicer CLI trên Linux
  có thể cần `xvfb`, và phải ghim phiên bản (OrcaSlicer 2.3.2 từng lỗi CLI `--slice`).
- **Model dạng mã (code-CAD)**: dựng chi tiết bằng script tham số (CadQuery/build123d, hoặc script FreeCAD như
  `_work/build_v3.py` đang làm) → diff được trên git, dựng lại được, review được. File `.FCStd` là nhị phân, git không diff.

## 2. Plan chuẩn hóa (đề xuất – theo thứ tự lợi/công)

### GĐ A – Mẫu dự án chuẩn (1 buổi) `[x]` (2026-10-23)
Mọi dự án CAD mới tạo từ `maker/robotics-cad/project-template/`, để `prepare-print.py` chạy ngay:
```
maker/<project>/            tên tiếng Anh, mọi thứ của dự án ở đây
  README.md  CLAUDE.md      mục tiêu, BOM, an toàn, bàn in, lịch sử (nội dung tiếng Việt)
  freecad/                  <model>.FCStd (chỉ trên máy), _rest.json, _sim.FCMacro, scripts/, images/,
                            check/ + backup/ (không lên git)
  print/                    print.yaml (hướng in + kiểm + bàn in); stl/, plates/ (file sinh, không lên git)
```
- Quy ước tên Label: linh kiện mua bắt đầu `CB_` / `LK_`; nhựa dẻo hậu tố `_TPU`; chi tiết đối xứng `_L`/`_R`
  → `components=`, `suffix` dùng glob chung, khỏi khai từng dự án.
- Lệnh `/new-project` sinh khung trên. Đặt tên tiếng Anh (Tuan 2026-10-23).

### GĐ B – Đưa dự án CAD vào git `[x]` (2026-10-23)
- Trước 2026-10-23: dữ liệu ở `D:\06_FreeCAD\`, không có git.
- Lựa chọn: (1) chuyển dự án vào `claude-workspace/maker/<du-an>/` + **Git LFS** cho `.FCStd/.step` (8 MB/lần lưu);
  (2) chỉ đưa `build/`, `ban-in.yaml`, README, ảnh lên git, FCStd giữ ngoài.
- **Tuan chốt (2026-10-23 chiều):** gom HẾT vào `maker/<project>/`; `.FCStd` chỉ trên máy (không LFS),
  backup 3 bản gần nhất ở `freecad/backup/`; mọi thứ khác (yaml, script, ảnh, README) lên git.

### GĐ C – "Release" bản in (KiBot/FCBot pattern) `[ ]`
- Khi `prepare-print` PASS và Tuan duyệt ảnh → tạo tag `<du-an>-vX.Y` + GitHub Release đính: 3MF từng bàn,
  `tong-quan.png`, `tong-quan-in.png`, BOM, changelog ngắn (sửa gì so với bản trước).
- Đăng MakerWorld/Printables: làm tay từ Release (không tự đăng – đăng ra ngoài phải Tuan duyệt).

### GĐ D – Tự chạy, không phải nhớ `[x]` (2026-10-23)
- **Cục bộ trước**: khi Lưu file `.FCStd` (theo dõi thời điểm sửa) → tự chạy `prepare-print` nền, kết quả là ảnh.
  Hoặc nút "Chuẩn bị in" trên Toolhub (đúng quy ước: tính năng mới → trang Toolhub).
- **GitHub Actions sau** (khi có GĐ B): chỉ chạy phần không cần Bambu (kiểm + xuất STL) trên runner Linux;
  phần cắt lớp chạy trên máy này (self-hosted runner) vì cần profile Bambu + Windows. Đánh đổi: tốn công dựng,
  lợi khi có nhiều người cùng sửa.

### GĐ E – Vòng học từ bản in thật (nối với harness-lab) `[x]` (2026-10-23)
- In xong: ghi 1 dòng vào `harness-lab/inbox.md` (in đạt? lỗi gì? sửa gì) bằng `/bai-hoc`.
- Mỗi lỗi in lặp ≥ 2 lần → thành quy tắc/ngưỡng (`nguong-kiem-tra.yaml`) hoặc bước kiểm mới.
- Việc đang treo: in `maker/in-3d/models/mau-dung-sai-a1` để xác nhận 0,2 mm; ngưỡng "mép sắc" 1 mm² và
  "chồng nhiễu" 0,1 mm³ đang TẠM (Claude đặt).

## 3. Đo tiến bộ
| Chỉ số | Hiện tại | Mục tiêu |
|---|---|---|
| Thời gian 1 vòng sửa → file in | ~1 phút máy + thời gian chờ người | ~1 phút, tự chạy khi Lưu |
| Lỗi phát hiện sau khi in (đáng lẽ bắt trước) | chưa đo | ghi qua `/bai-hoc`, giảm dần |
| Số bước tay mỗi lần in | xuất STL, xếp bàn, cắt lớp: đã tự động | chỉ còn duyệt ảnh + bấm in |

## 4. Việc Tuan cần quyết
- [x] GĐ B: mọi thứ trong `maker/<project>/` (`freecad/` + `print/`), FCStd chỉ trên máy (2026-10-23)
- [x] GĐ D: làm cả hai – Toolhub → Dự án: **Chuẩn bị in** + **Tự chạy khi Lưu** (`scripts/watch.py`)
- [x] GĐ A: `maker/robotics-cad/project-template/` + lệnh `/new-project`; dự án mẫu: `maker/pushrod-arm/`
- [x] GĐ E: lệnh `/print-result` → README dự án + `harness-lab/inbox.md`
- [ ] GĐ C (Release): chưa làm

## Nguồn
- FCBot – tự sinh file sản xuất từ FreeCAD, Docker cho CI: https://github.com/asymworks/fcbot
- FreeCAD wiki – Headless FreeCAD: https://wiki.freecad.org/Headless_FreeCAD
- Ví dụ workflow GitHub Actions xuất STEP/STL từ FCStd: https://deepwiki.com/0x007E/tpd/4.1-github-actions-workflows
- OrcaSlicer CLI: https://www.orcaslicer.com/wiki/cli/cli_actions ; tham chiếu bên thứ ba: https://printago.io/blog/orca-slicer-cli-reference
- Lỗi CLI OrcaSlicer 2.3.2 (ghim phiên bản): https://newreleases.io/project/github/linuxserver/docker-orcaslicer/release/v2.3.2-ls22
- KiBot (mẫu tự động hóa + release cho KiCad): https://kibot.readthedocs.io/en/latest/
- Mẫu repo + workflow release KiCad: https://github.com/bob-swinkels/KiCad-Project-Skeleton/blob/main/README.md
- Bambu Studio CLI: https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage
