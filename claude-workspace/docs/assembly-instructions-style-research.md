# Nghiên cứu: cách làm ảnh hướng dẫn lắp ráp rõ ràng (cho học sinh)

Viết 2026-10-25 cho `maker/pushrod-arm/ASSEMBLY.md` – Tuan: "chưa rõ nét và màu sắc chưa phù hợp".
Nhãn: **[nguồn gốc]** = bài báo / tài liệu hãng; **[đo]** = mình thử trên model STLab.

## 0. Kết luận nhanh
1. **Ảnh "thao tác" tốt hơn ảnh "cấu trúc"** [nguồn gốc]: tách chi tiết mới ra khỏi chỗ lắp, vẽ **đường dẫn** tới chỗ gắn.
   Ảnh cũ của mình là ảnh cấu trúc (chi tiết đã nằm đúng chỗ) – người xem phải tự so với bước trước.
2. **Chi tiết mới phải thấy rõ; phần đã lắp chỉ cần hiện một phần làm bối cảnh** [nguồn gốc]. Ảnh cũ làm mờ (trong suốt
   75 %) **toàn bộ** cánh tay → rối, nhòe.
3. **Mỗi bước 1 chi tiết chính** (kèm vít/nhỏ); **thao tác lặp lại không vẽ lại chi tiết** [nguồn gốc] → xi-lanh khuỷu
   ghi "làm giống xi-lanh vai" thay vì 3 bước vẽ lại.
4. Hãng CyberBrick (cùng hệ linh kiện) dùng **khối màu trung tính + viền đậm**, **1 màu nhấn**, **số bước to**, **nhãn
   gọi tên có đường dẫn** (vd. "M2.5x6 BHCS Machine Screw"), mũi tên trước → sau, nét đứt chỉ chỗ luồn [nguồn gốc].
5. Thử trên model [đo]: viền đen (FreeCAD "Flat Lines") + xám nhạt cho phần đã lắp + vàng STLab cho chi tiết mới + tách
   chi tiết + nét đứt + chụp 2× rồi thu nhỏ + tự cắt khung → rõ hơn hẳn (ảnh so sánh dưới).

## 1. Nguồn và điều rút ra
| Nguồn | Điều rút ra |
|---|---|
| Agrawala, Phan, Heiser, Haymaker, Klingner, Hanrahan, Tversky – *Designing Effective Step-By-Step Assembly Instructions*, ACM SIGGRAPH 2003 / ToG 22(3) 828–837 [nguồn gốc] | Nhóm chi tiết theo cụm (hierarchy); mỗi ảnh gắn **1 chi tiết chính** + nhiều chi tiết nhỏ; bỏ thao tác lặp lại sau vài lần đầu; **action diagram** (tách + guidelines) tốt hơn structural diagram; hướng nhìn tự nhiên; **chi tiết mới phải thấy**, một phần chi tiết cũ thấy để làm bối cảnh |
| Heiser, Phan, Agrawala, Tversky, Hanrahan – *Identification and Validation of Cognitive Design Principles for Automated Generation of Assembly Instructions*, AVI 2004 [nguồn gốc – tóm tắt] | Hướng dẫn theo các nguyên tắc trên: thời gian lắp **−35 %**, lỗi **−50 %** (bài lắp nội thất) |
| CyberBrick L-ONE Desktop Robotic Arm Assembly Guide (`community/cyberbrick-official/pdf/`) [nguồn gốc] | Hình nét đen trắng, tách chi tiết, đường đứt chỉ hướng; mỗi khung 1 thao tác, chữ ngắn |
| CyberBrick Mini T Assembly Guide [nguồn gốc] | Khối kem/xám + viền đậm; số bước rất to; nhãn có đường dẫn; mũi tên trước → sau; nét đứt xanh chỉ chỗ luồn; màu chỉ cho dây (đỏ) / điểm chú ý |

## 2. Quy cách ảnh mới (đề xuất – chờ Tuan duyệt)
| Mục | Cũ | Mới |
|---|---|---|
| Chi tiết đã lắp | màu gốc, trong suốt 75 % | **xám nhạt đặc** `#D3DDD8` (STLab "line"), chỉ hiện cụm liên quan |
| Chi tiết mới | màu chọn xanh nhạt của FreeCAD | **vàng STLab** `#E8B33A` (STLab "highlight") |
| Viền | không | **viền đen-xanh** `#16231D`, FreeCAD `Flat Lines`, dày 4 px ở ảnh 2× |
| Thao tác | chi tiết nằm sẵn đúng chỗ | **tách chi tiết theo hướng lắp** + **đường nét đứt** tới chỗ gắn |
| Khung | cả cánh tay, vật nhỏ | **cụm đang lắp**, tự cắt khung, chừa lề 8 % |
| Độ nét | 1200 × 900 | chụp **2400 × 1800** rồi thu nhỏ 1200 × 900 |
| Hướng nhìn | isometric cố định | isometric; bước bắt vít từ dưới → nhìn từ dưới |
| Bước lặp | vẽ lại (xi-lanh khuỷu 15–17) | "làm giống bước 12–14" + 1 ảnh xong |

Mẫu: `maker/pushrod-arm/freecad/images/assembly-style-proto/compare-old-new.png`, `new-style-3-steps.png`
(đã áp dụng: `freecad/scripts/render_assembly_steps.py`, 32 bước – 2026-10-25).

## 3. Việc còn lại khi áp dụng cho 34 bước
- Khai **hướng tách + khoảng cách** cho từng chi tiết từng bước (bảng trong script) và **cụm bối cảnh**.
- Nhãn gọi tên (tên chi tiết, "×4 M2.5×16") vẽ lên ảnh bằng PIL hoặc để trong khung "Cần lấy" của PDF.
- Gộp bước lặp (15–17 → 1 bước), giữ ~30 bước.

## Nguồn
- [Designing Effective Step-By-Step Assembly Instructions – Stanford Graphics](https://graphics.stanford.edu/papers/assembly_instructions/)
  · [PDF (Columbia TC)](https://www.tc.columbia.edu/faculty/bt2158/faculty-profile/files/signingeffectivestepbystepassemblyinstructions.pdf)
  · [SIGGRAPH history](https://history.siggraph.org/?p=115936)
- [Identification and Validation of Cognitive Design Principles… – Stanford Graphics](https://graphics.stanford.edu/papers/assembly_instructions_study/)
- CyberBrick official: `community/cyberbrick-official/pdf/L-ONE_Desktop_Robotic_Arm_Assembly_Guide.pdf`,
  `CyberBrick Mini T Assembly Guide.pdf`.
