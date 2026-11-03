# Keycap MX in FDM, khe in-place PETG, mốc Tết 2027 (tra 2026-11-03)

Codex tra web; Claude chưa mở từng link. Phục vụ maker/switch-clicker và maker/tet-goat-flexi.

## 1. Keycap MX

- 3,6 mm của Cherry = trục chữ thập nhô trên mặt vỏ trên khi nghỉ (mặt vỏ → đỉnh chữ thập), không phải độ sâu lỗ keycap. Nguồn: https://datasheet.octopart.com/MX1A-11NW-Cherry-datasheet-34676.pdf ; https://github.com/techmech-keeb/OLSK60_v2/blob/main/docs/reference/cherry-mx-switch-spec.md
- Suy ra (hình học, chưa phải số đo): hành trình 4,0 → đỉnh chữ thập xuống dưới mặt vỏ 0,4 khi nhấn hết → ống keycap phải lọt được vào lỗ vỏ hoặc chạm vỏ sớm. Số chạm thực tế: TODO – xem khi cắm thử switch (mẫu stem-coupon).
- KeyV2: `$stem_slop = 0.35`, `$stem_inner_slop = 0.2`, `$stem_support_type = "tines"` https://github.com/rsheldiii/KeyV2/blob/master/src/settings.scad#L669-L706 ; `$stem_inset` là độ lùi của stem, không phải độ sâu cắm https://github.com/rsheldiii/KeyV2/blob/master/src/key_transformations.scad#L866-L872 ; mẹo kiểm va chạm switch https://github.com/rsheldiii/KeyV2/blob/master/TIPS_AND_TRICKS.md
- dennisleexyz/keycaps: ống stem Ø 5,5 vừa nhiều dòng switch; Tol PLA 0,05 (in phẳng) / 0,10 (in xoay), PCTG 0,10 (phẳng) – kết quả của tác giả, không phổ quát. https://github.com/dennisleexyz/keycaps
- keycaps.dev: in bộ hiệu chỉnh 0,00–0,20 rồi thử nhẹ trên switch thật https://keycaps.dev/guides/3d-printing-keycaps
- Hướng in: dennisleexyz khuyên in phẳng, stem hướng lên; Reddit có người in 45° (PLA, nozzle 0,2) – kinh nghiệm cá nhân. Gãy ống stem là lỗi hay gặp; KeyV2 dùng "tines" để gia cố. https://www.reddit.com/r/ErgoMechKeyboards/comments/1n10lyw/have_anybody_tried_here_to_fdm_keycaps/
- Đối chiếu STLab: stem-coupon đang thử lỗ chữ thập 4,33 / 4,43 / 4,53 (≈ Tol 0,05 / 0,10 / 0,15 mỗi bên trên 4,23) – nằm trong khoảng cộng đồng.

## 2. Khe khớp in liền (print-in-place)

- Bản lề A1 + PLA: khe ≥ 0,2 quanh chốt chạy được (Loftsmith hinge test https://loftsmith.com/generators/hinge-test); hướng dẫn chung 0,35–0,45, máy chỉnh tốt 0,3 (https://loftsmith.com/guides/print-in-place-hinge).
- PETG cần thêm ~0,05 XY so với PLA (https://buildcad.ai/3d-print-tolerance); PETG cầu dễ võng (diễn đàn https://www.reddit.com/r/BambuLab/comments/13580xi/).
- Bambu chưa công bố bảng khe in-place chính thức: TODO. Khe Z khuyến nghị: TODO. Bù chân voi chỉ giúp mép đáy, không thay khe Z (https://forum.bambulab.com/t/solved-multicolour-gap-on-first-layer/85331/2).
- Lưu ý: nguồn không thống nhất "khe" là tổng hay mỗi bên.
- Đối chiếu STLab: mẫu thử dê dùng khe hướng kính MỖI BÊN 0,4 / 0,5 / 0,6, khe Z 0,4, khe thân 0,6 – phía an toàn hơn cộng đồng PLA, hợp PETG.

## 3. Tết 2027

- Mùng 1 Tết Đinh Mùi: thứ Bảy 06/02/2027; nghỉ từ 04/02 (https://baochinhphu.vn/nghi-tet-am-lich-2027-keo-dai-7-ngay-nghi-quoc-khanh-4-ngay-102261010095648278.htm).
- Đinh Mùi = năm con Dê ở VN (tiếng Anh hay gọi Sheep) (https://amlichvietnam.vn/kien-thuc/lich-am/nam-2027-la-nam-con-gi).
- Mua sắm Tết: phần lớn 1–2 tuần trước (53 %, Ipsos https://www.ipsos.com/en-vn/tet-2026-vietnam-festive-hearts-sharper-carts); quà doanh nghiệp 2–3 tuần (32 %) và 1 tháng (28 %) trước (https://www.global-market-surfer.com/pickup/detail/223?l=en).
- MakerWorld đã có mẫu dê 2027 (Year of the Goat, kẹp khăn giấy dê, móc khóa/tượng dê mini PLA) – qua polyzon.org: https://polyzon.org/en/model/makerworld/mw-3132742 , mw-3311465 , mw-3385985 → cạnh tranh có sẵn; STLab khác biệt bằng flexi in liền + nét Việt.
- Chưa thấy listing đồ in 3D Tết kiểm chứng được ở VN (listing "3D" trên Shopee thường là thiệp nổi/lì xì, không phải in 3D): TODO.

## 4. Mốc cho STLab (Claude)

| Mốc | Ngày | Việc |
|---|---|---|
| Chốt khe + dựng dê hoàn chỉnh | trước 20/11/2026 | sau khi in mẫu thử |
| In mẫu thật + ảnh + đăng MakerWorld | trước 10/12/2026 | đăng sớm để lấy lượt tải trước mùa |
| Nhận đặt quà doanh nghiệp/trường | từ 06/01/2027 (1 tháng trước) | in sỉ, giá sỉ /quote |
| Bán lẻ cao điểm | 23/01 – 03/02/2027 | |
