# spacer-tubes – ống trụ rỗng (spacer)

| File | Ø ngoài | Ø lỗ | Cao |
|---|---|---|---|
| tube-od5-id2.2-h20 | 5 mm | 2,2 mm | 20 mm |
| tube-od10-id2.2-h20 | 10 mm | 2,2 mm | 20 mm |
| tube-od10-id2.4-h20 | 10 mm | 2,4 mm | 20 mm |

- CAD đo được: `solidcraft/spacer-tubes.sc` (mỗi ống 1 component). Sửa số: `solidcraft/params.json` → `python build_tubes.py`.
- In: `solidcraft/plates/p1-spacer-tubes/p1-spacer-tubes.3mf` (PETG, 0,16 mm, brim 4 mm, không support).
- Lỗ vẽ đúng số danh nghĩa; in FDM lỗ nhỏ thường hụt ~0,1–0,2 mm → cần lỗ lọt thì khoan/ doa lại hoặc tăng `id`.
