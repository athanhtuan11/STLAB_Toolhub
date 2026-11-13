# spacer-tubes – ống trụ rỗng (spacer)

| File | Ø ngoài | Ø lỗ | Cao |
|---|---|---|---|
| tube-od10-id3.4-h15 | 10 mm | 3,4 mm | 15 mm |

- CAD đo được: `solidcraft/spacer-tubes.sc` (mỗi ống 1 component). Sửa số: `solidcraft/params.json` → `python build_tubes.py`.
- In: `solidcraft/plates/p1-spacer-tubes/p1-spacer-tubes.3mf` (PETG, 0,16 mm, brim 4 mm, không support).
- Các ống cũ (od5/od10, id2.2/2.4/4.4, cao 20) ở `backup/20261113-spacer-tubes-cu/` (chỉ trên máy).
- Lỗ vẽ đúng số danh nghĩa; in FDM lỗ nhỏ thường hụt ~0,1–0,2 mm → cần lỗ lọt thì khoan/ doa lại hoặc tăng `id`.
