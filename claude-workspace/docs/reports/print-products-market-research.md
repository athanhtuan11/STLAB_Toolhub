# Nghiên cứu mẫu in 3D cho cộng đồng và thị trường địa phương

Ngày tra cứu: 2026-11-02. Phạm vi: thiết kế mới của STLab để chia sẻ file và bán sản phẩm in tại Đức Trọng/Đà Lạt. Đây là nghiên cứu định hướng, không phải báo giá hay xác nhận pháp lý.

## 1. Boi canh STLab

- **Mục tiêu cộng đồng:** đăng mẫu hữu ích, dễ in, có hướng dẫn và file nguồn/profile đáng tin; lượt in, đánh giá và phản hồi giúp tăng uy tín, tạo vòng lặp cải tiến.
- **Mục tiêu địa phương:** bán vật phẩm hữu ích/quà tặng và nhận đơn tùy biến tên, logo do khách cung cấp. Thu nhập thực tế phải đo bằng đơn hàng và thời gian làm; điểm/quà nền tảng không phải doanh thu chắc chắn.
- **Hai mục tiêu hỗ trợ nhau:** chia sẻ bản phổ thông để được thử nghiệm và nhận góp ý; phát triển biến thể cá nhân hóa, bộ kit hoặc hoàn thiện tại chỗ để bán. Không điều kiện hóa quyền sử dụng file cộng đồng bằng việc mua hàng.
- **Giới hạn sản xuất:** Bambu Lab A1, thể tích in 256 × 256 × 256 mm; Bambu PETG Basic và bàn Textured PEI. AMS lite có hay không: chưa xác nhận; mẫu một màu không cần AMS, mẫu nhiều màu ghi rõ ở bảng. Tránh support trong hình học STL; người vận hành tự quyết support trong Bambu Studio. [S1]
- Thiết kế mới bằng FreeCAD script tham số, ảnh/render bằng Blender. Ước tính cuối cùng lấy từ lát cắt/3MF và tab `/quote` (markup 60%, dự phòng hỏng 15%, giá sỉ từ 50/100 chiếc giảm 10%/15%); không coi đây là giá bán đã duyệt.
- **Ranh giới bản quyền:** model cộng đồng chỉ đọc để học nguyên lý/fit trong fit-library. Mẫu đăng hoặc bán phải là thiết kế mới, không đăng remix, không in bán model người khác theo Standard Digital File License của MakerWorld. [S2]
- Bối cảnh nội bộ đã đối chiếu: `docs/reports/3d-print-cost-quote-oss.md` nêu cách dùng `/quote`; `docs/reports/community-for-repo-growth.md` và `docs/reports/reverse-engineering-model-cong-dong.md` nêu nguyên tắc chỉ đọc model cộng đồng; `docs/COMMUNITY.md` ghi quy tắc nguồn/license; `maker/CLAUDE.md` ghi ranh giới an toàn; `tools/model-study/fit-library/fit_lib.py` và `tools/model-study/fit-library/fits.json` là tài liệu nội bộ để tra fit đã lưu.

## 2. Nen tang cong dong

| Nền tảng | Cơ chế và cơ hội | Tệp người dùng / điểm mạnh | Công đăng, rủi ro |
|---|---|---|---|
| **MakerWorld** | Điểm thưởng/đổi quà và Boost là các cơ chế khuyến khích creator; điểm, vật phẩm đổi, điều kiện và giá trị quy đổi có thể đổi theo chương trình. Exclusive/Original, Print Profile (file dự án/cấu hình in), MakerLab/parametric customizer và mục Trending giúp phân phối/khám phá mẫu. Tác giả cần tự đọc điều khoản license ở thời điểm đăng; SDL tiêu chuẩn không cấp quyền thương mại cho người tải mẫu. Chủ sở hữu thiết kế mới của STLab có thể tự khai thác sản phẩm của mình trong phạm vi quyền và thỏa thuận nền tảng, không lấy quyền đó từ model người khác. | Phù hợp nhất với A1/Bambu; file có profile sử dụng được ngay giúp giảm ma sát tải/in. Thứ hạng Trending và cơ chế xếp hạng không công bố đầy đủ. | Công trung bình: cần profile đã thử, ảnh, mô tả, hướng dẫn và trả lời bình luận. Tuân thủ bản quyền, quyền hình ảnh/logo, tiêu chuẩn chất lượng và quy tắc nội dung. Trang chính sách/trang điểm bị chặn khi truy cập tự động; chi tiết đổi thưởng, cấp nhãn và license cần xác nhận trực tiếp trước khi đăng. [S2] |
| **Printables** | Prusameters đổi lấy phần thưởng trong hệ sinh thái Prusa; Printables Club hỗ trợ creator bằng membership trả phí theo điều kiện nền tảng. Không xem điểm là tiền mặt/thu nhập đảm bảo. | Cộng đồng đa máy in; tệp STL/3MF và trang hướng dẫn có ích. | Công trung bình; cần bản xuất phổ thông, hướng dẫn máy/nhựa rõ, license riêng từng mẫu. Cơ chế điểm và điều khoản Club có thể thay đổi. [S3] |
| **Thingiverse** | Kênh chia sẻ/tìm model; không dự toán thu nhập trực tiếp từ lượt tải. Quyền tái sử dụng phụ thuộc license mà tác giả chọn cho từng thiết kế (thường gặp Creative Commons). | Kho model lâu đời, người dùng rộng; tốt để tăng độ phủ cho file miễn phí. | Công thấp-vừa nếu đăng bộ file/hướng dẫn; kiểm quyền trước khi dùng tham khảo. Không mặc định license cho phép thương mại. [S4] |
| **Cults3D** | Marketplace bán file số; doanh thu là bán file sau phí/điều khoản marketplace, không phải bán sản phẩm vật lý tại STLab. Tỷ lệ chia và phương thức chi trả hiện hành: cần xác nhận. | Người mua tìm STL/3D-printable files; phù hợp nếu STLab có bộ file độc đáo và ảnh sản phẩm tốt. | Công vừa-cao: đóng gói file, ảnh, bản mô tả, hỗ trợ người mua, quản lý bản quyền. [S5] |
| **Thangs** | Tìm kiếm/khám phá model và các hình thức hỗ trợ creator/membership tùy chương trình. Không ghi nhận một mức chia sẻ doanh thu hay quy mô người dùng chưa kiểm chứng. | Có thể làm kênh bổ sung để được tìm thấy; cần đối chiếu lượt truy cập thực tế. | Công thấp-vừa khi tái sử dụng gói phát hành do STLab sở hữu; xác minh điều kiện thương mại và thanh toán trước khi dựa vào doanh thu. [S6] |

**So sánh nhanh:** điểm/quà: MakerWorld, Printables; bán file: Cults3D và chương trình creator phù hợp của Thangs (điều kiện cần kiểm); Thingiverse chủ yếu là độ phủ; bán vật phẩm tại địa phương là kênh riêng. Không có số liệu người dùng đồng nhất, cùng kỳ và kiểm chứng được cho cả năm nền tảng nên xếp quy mô định tính, không xếp hạng bằng số. Công đăng thường thấp với file STL đơn giản, tăng lên khi có profile đa máy, nhiều biến thể, ảnh/video, hướng dẫn và hỗ trợ sau đăng. [S2–S6]

**Giới hạn kiểm chứng:** trang MakerWorld, Printables, Cults3D và Thangs chặn một số truy cập tự động (403/404); bảng trên chỉ nêu chức năng khái quát. Trước khi phát hành cần xem trực tiếp điều khoản cập nhật, đặc biệt điểm/quà, phí, payout, quyền sử dụng, nhãn Exclusive/Original và giới hạn đăng. Không tải lại hoặc sao chép model người khác.

## 3. Xu huong mau in

- **Nhóm đáng theo dõi trong 2025–2026:** print-in-place; articulated/posable; fidget; hệ modular như Gridfinity/Multiboard; organizer; đèn/decor; phụ kiện có tham số hóa. Đây là danh mục/quan sát định tính, không phải thống kê tải/Boost; chưa có snapshot so sánh theo kỳ cho MakerWorld/Printables. [S7]
- **Trang mẫu có cơ hội chuyển đổi tốt:** ảnh chính rõ và ảnh vật thể thật; clip ngắn thể hiện thao tác; profile đúng máy/vật liệu; hướng dẫn lắp, hướng in và vị trí support; file nguồn/biến thể được đặt tên rõ; mô tả nói rõ kích thước thực sau khi slice, mục đích và hạn chế; cập nhật khi người dùng báo lỗi. Đây là checklist biên tập để thử nghiệm, không phải thuật toán xếp hạng được xác nhận.
- **Hướng STLab:** đi vào ngách địa phương và giáo dục, không chạy đua bản sao fidget/đồ chơi phổ thông. Ưu tiên mẫu ít chi tiết, 1 màu, ít support, có thể đổi chữ/kích thước bằng tham số. Với mẫu nhiều màu, tính riêng thời gian purge và ghi cần AMS; A1 có thể in một màu nếu đổi filament thủ công nhưng không mặc định cách làm đó tối ưu.
- Không có số tải/Boost 2025–2026 đã chụp và kiểm tra được cho từng mẫu: không đưa số. Tạo bảng theo dõi sau khi Tuan chọn mẫu: link, ngày, lượt tải/print/boost công khai, profile, license, ngày chụp.

## 4. Danh muc san pham

Thời gian/khối lượng dưới đây là **khoảng lập kế hoạch rất sơ bộ**, không phải số đo từ model đã slice; phụ thuộc hình học, infill, layer, nozzle và profile. Xác nhận bằng Bambu Studio trước khi báo giá. PETG phù hợp/không phù hợp là đánh giá ứng dụng sơ bộ, không phải chứng nhận.

| Nhóm | Ví dụ mẫu mới | Hợp đăng cộng đồng | Hợp bán địa phương | Thời gian + khối lượng ước tính | Độ khó | PETG phù hợp? | Rủi ro chính |
|---|---|---:|---:|---|---|---|---|
| Gia dụng/organizer | Khay bàn lắp ghép, giá treo nhẹ | Cao | Cao | 0.5–3 h; 20–100 g | Thấp-vừa | Có | Kích thước/tải phải thử |
| Đồ chơi + fidget | Cơ cấu clicker nguyên bản, puzzle | Cao | Vừa | 0.5–3 h; 15–80 g | Vừa | Có, có giám sát | Chi tiết nhỏ, cạnh/kẹp tay |
| STEAM: mô hình/kit | Bộ truyền động bánh răng học tỉ số | Cao | Cao | 1–4 h; 40–180 g | Vừa-cao | Có | Chi tiết nhỏ; cần bài hướng dẫn |
| Quà Đà Lạt/Lâm Đồng | Bookmark/nametag họa tiết địa hình, hoa/cà phê nguyên bản | Cao | Cao | 0.3–2 h; 8–50 g | Thấp | Có | Tránh logo/biểu trưng không được phép |
| Nông nghiệp | Nhãn cây, kẹp cành, khay ươm mô-đun | Cao | Cao | 0.5–4 h; 15–180 g | Thấp-vừa | Có, thử ngoài trời | UV/nhiệt/độ bền theo mùa chưa thử |
| Quán cà phê/cửa hàng | Đế QR, kệ menu, bảng tên | Cao | Cao | 0.5–3 h; 20–120 g | Thấp | Có | Logo/chữ do khách xác nhận quyền |
| Điện thoại/máy tính/bàn học | Giá đỡ điện thoại, kẹp dây, kê laptop nhỏ | Cao | Cao | 0.5–4 h; 20–160 g | Vừa | Có, tránh nơi nóng | Tải, trượt, nhiệt thiết bị |
| Xe máy/xe đạp | Móc treo đồ tĩnh, kẹp phụ kiện không chịu tải | Vừa | Vừa | 0.5–3 h; 15–120 g | Vừa | Chỉ vị trí mát, không an toàn-critical | Rung, nắng/nhiệt, hỏng gây tai nạn |
| Đèn + decor | Chụp đèn LED/lithophane decor | Cao | Vừa | 1–5 h; 30–200 g | Vừa | Có điều kiện | Nhiệt/nguồn điện; dùng LED phù hợp, không chạm bóng nóng |
| Vỏ hộp điện tử | Hộp ESP32/cảm biến, nắp thay thế | Cao | Cao | 1–4 h; 25–160 g | Vừa | Có | Không thay vỏ cách điện/chứng nhận; kiểm fit |
| CyberBrick/robot | Giá giữ cảm biến, phụ kiện lắp robot | Cao | Cao | 0.5–3 h; 15–120 g | Vừa | Có | Chỉ dùng giao diện đã đo/thử; không đoán fit |
| Phụ tùng thay thế | Núm vặn, chốt, nắp, chân đệm không critical | Vừa | Cao | 0.5–3 h; 10–100 g | Vừa | Có tùy vị trí | Không thay chi tiết chịu lực/an toàn khi chưa kiểm |
| Thú cưng | Móc tên, hộp/túi phụ kiện ngoài tầm nhai | Vừa | Vừa | 0.5–2 h; 10–70 g | Thấp-vừa | Có điều kiện | Không dùng làm đồ nhai/tiếp xúc thức ăn |
| Văn phòng/trường học | Kẹp giấy, thước góc học tập, khay dụng cụ | Cao | Cao | 0.5–3 h; 10–100 g | Thấp-vừa | Có | Cạnh sắc/chi tiết nhỏ |
| Phụ kiện máy in 3D | Giá dụng cụ, clip spool, hộp nozzle | Cao | Cao | 0.5–3 h; 15–120 g | Vừa | Có | Tránh chi tiết nóng/chuyển động nguy hiểm |
| Cà phê/hoa: phụ trợ cửa hàng | Kẹp túi cà phê, tag quà, vòng đánh dấu chậu | Cao | Cao | 0.3–2 h; 8–60 g | Thấp | Có, không tiếp xúc trực tiếp thực phẩm | Không tuyên bố food-safe; bản quyền hình ảnh |
| Modular shop display | Chân kê sản phẩm, móc trưng bày theo rãnh | Vừa | Cao | 1–4 h; 30–200 g | Vừa | Có | Tải và ổn định phải thử tại chỗ |

## 5. Thi truong dia phuong

| Kênh tham khảo | Cách dùng / giá |
|---|---|
| Shopee: [tìm “móc khóa in 3D”](https://shopee.vn/search?keyword=m%C3%B3c%20kh%C3%B3a%20in%203D), [“đồ in 3D”](https://shopee.vn/search?keyword=%C4%91%E1%BB%93%20in%203D) | Trang tìm kiếm truy cập được nhưng giá/biến thể động không được trích xuất đáng tin cậy; chưa ghi khoảng giá để tránh bịa. Chụp lại ít nhất vài listing cùng loại, vật liệu, kích thước và ngày trước khi định giá. |
| Facebook Marketplace: [tìm đồ in 3D](https://www.facebook.com/marketplace/search/?query=do%20in%203D) | Trang Marketplace phụ thuộc vị trí/đăng nhập; kết quả lấy được đang ở vị trí mặc định khác Việt Nam, không dùng làm giá Đức Trọng. Tìm theo địa điểm Đức Trọng/Đà Lạt khi kiểm tra thủ công. |
| TikTok Shop: [tìm “in 3D”](https://www.tiktok.com/shop/search?q=in%203D) | Trang tìm kiếm tự động chuyển hướng/không trả danh sách hàng; không có giá được xác minh. Dùng để quan sát video và nhu cầu, đối chiếu giá listing đang bán thủ công. |

**Kết luận giá:** tại lần tra cứu 2026-11-02 chưa xác minh được listing so sánh đồng nhất ở cả ba sàn; không nêu giá bán thị trường. Sau khi có link sản phẩm tương đương, dùng `/quote` để tính giá vốn và áp dụng chính sách STLab; không suy ra giá bán chỉ từ gam nhựa.

**Kênh bán thử:** fanpage STLab và hội nhóm địa phương; quầy/cửa hàng quà lưu niệm; quán cà phê/roastery (đế QR, tag, display mang thương hiệu khách); trường học và lớp STEAM; nông trại/vườn hoa (nhãn, kẹp, khay ươm); sự kiện/Open Lab cho khách thử và đặt cá nhân hóa. Đây là kênh đề xuất, chưa xác minh thỏa thuận với đơn vị nào. Địa bàn có thể gắn chủ đề du lịch, cà phê, hoa, rau/nông trại và sân bay Liên Khương; xác nhận thông tin điểm đến/kênh tại [cổng du lịch Đà Lạt](https://dalat.vn/) và [Cảng hàng không Liên Khương](https://acv.vn/lien-khuong-airport) trước chiến dịch (truy cập 2026-11-02).

Đơn theo tên/logo: khách gửi nội dung và xác nhận quyền sử dụng; STLab làm bản xem trước, xác nhận màu/thời gian/giá và chỉ in sau khi Tuan duyệt. Tách phí thiết kế tùy chỉnh khỏi phí sản xuất; không dùng nhận diện thương hiệu/trường/quán nếu chưa được cho phép.

## 6. Phap ly va an toan

- **Bản quyền/thương hiệu:** không dùng nhân vật, logo, nhãn hiệu, tác phẩm hay hình dáng đặc trưng có bản quyền để tạo sản phẩm thương mại nếu chưa có quyền. Không tải model rồi remix/đăng lại/bán bản in. Chỉ dùng tài sản STLab tự thiết kế hoặc có văn bản cấp phép cho đúng mục đích. Tra cứu văn bản tại [Cơ sở dữ liệu quốc gia về văn bản pháp luật](https://vbpl.vn/) và kiểm license của từng nền tảng (truy cập 2026-11-02). [S2, S4]
- **Đồ chơi trẻ em:** không quảng cáo là đồ chơi an toàn/chứng nhận khi chưa đánh giá. Cảnh báo chi tiết nhỏ gây hóc, cạnh sắc, kẹp/nghiền ngón; cần xác định độ tuổi và thử nghiệm phù hợp trước khi bán cho trẻ. Tra cứu QCVN 3:2019/BKHCN tại [Cổng thông tin tiêu chuẩn đo lường chất lượng](https://tcvn.gov.vn/) và cơ sở văn bản nêu trên; phạm vi áp dụng/phiên bản hiện hành cần xác minh trước khi kinh doanh.
- **Tiếp xúc thực phẩm:** không gọi PETG Basic hay chi tiết FDM là “food safe”. Bề mặt lớp in có khe, vệ sinh/vi sinh, màu/phụ gia và điều kiện dùng đều ảnh hưởng; không thiết kế đồ chứa/tiếp xúc trực tiếp thực phẩm để bán nếu chưa có vật liệu, quy trình và đánh giá phù hợp. Hộp/đế đặt bên ngoài vật chứa cũng không nên mô tả như vật liệu tiếp xúc thực phẩm. [S8]
- **Nhiệt/ngoài trời/xe:** PETG không đồng nghĩa chịu được mọi nắng nóng; nhiệt độ làm mềm, lão hóa UV và tải phụ thuộc đúng cuộn vật liệu, hình học và môi trường. Không gắn lên vị trí nóng/rung/chịu lực của xe máy, không dùng làm chi tiết bảo vệ/an toàn. Thông số PETG Basic theo datasheet lô vật liệu và thử nghiệm thực địa: xác minh trước khi ghi nhiệt độ/tuổi thọ; không đặt ngưỡng nhiệt ở đây. [S8]
- **Kinh doanh online/hộ kinh doanh:** cần rà soát đăng ký kinh doanh, thuế, hóa đơn và nghĩa vụ thông báo/đăng ký sàn theo hình thức hoạt động và văn bản đang có hiệu lực; không tự áp ngưỡng miễn/đăng ký khi chưa kiểm văn bản hiện hành. Nguồn tra cứu chính thức: [Cổng văn bản Chính phủ](https://vanban.chinhphu.vn/), [Bộ Công Thương](https://moit.gov.vn/) và [Cổng quản lý hoạt động thương mại điện tử](https://online.gov.vn/) (truy cập 2026-11-02). Tuan cần xác nhận với cơ quan thuế/đăng ký địa phương trước khi vận hành thường xuyên.

## 7. Quy trinh STLab

| Bước | Claude/agent có thể chuẩn bị | Tuan tự làm/duyệt |
|---|---|---|
| 1. Chọn ý tưởng | Tóm tắt nhu cầu, kiểm nguồn/license, liệt kê rủi ro và spec cần hỏi | Chọn nhóm khách, mức ưu tiên, không dùng tài sản thiếu quyền |
| 2. Dựng tham số | Viết script FreeCAD và biến thể theo spec đã được duyệt; render Blender | Duyệt dáng/fit và các kích thước chức năng; số chưa có nguồn để TODO |
| 3. In thử A1 | Chuẩn bị STL/3MF và checklist kiểm in; không tự điều khiển máy vật lý | Chọn PETG Basic/profile, xử lý support trong Bambu Studio, in và ghi lỗi/khối lượng/thời gian thực |
| 4. Nội dung phát hành | Soạn ảnh/render, hướng dẫn, mô tả tiếng Anh + tiếng Việt, tag, file nguồn; chuẩn bị 3MF và profile A1 PETG sau khi thử | Chọn license, rà bản quyền/ảnh, duyệt trang và tự bấm đăng |
| 5. Bán | Chuẩn bị tùy biến tham số, tính báo giá qua `/quote`, lưu thông tin đơn theo quy trình STLab | Duyệt mẫu cuối, giá/chiết khấu, đơn hàng, cam kết khách hàng và tự giao dịch |

Phân vai theo quyền hiện hành của workspace: agent chỉ xử lý mã/spec được giao; không tự quyết kích thước, dung sai, an toàn, giá bán hoặc đăng công khai. Không tự lấy model người khác làm nền cho mẫu phát hành.

## 8. De xuat xep loi/cong

Xếp theo khả năng vừa chia sẻ vừa thử bán, tính địa phương/STEAM, công và rủi ro; thời gian thiết kế là ước tính cho mẫu đơn giản, chưa phải cam kết. Năm mục đầu là shortlist đề xuất, không phải phê duyệt triển khai. Thời gian/khối lượng in là mục tiêu ban đầu cần kiểm bằng slicer; để ưu tiên dưới 3 giờ phải giảm/đổi hình học nếu lát cắt vượt ngưỡng.

| # | Sản phẩm cụ thể | Nhóm | Lợi cộng đồng | Lợi bán địa phương | Công thiết kế (giờ) | Cần AMS? | Rủi ro | Nguồn/gợi ý |
|---:|---|---|---|---|---:|---|---|---|
| 1 ★ | Bộ nhãn cây tham số (tên cây/QR tùy chọn) | Nông nghiệp | File hữu ích, biến thể dễ | Vườn ươm/nông hộ đặt lô nhỏ | 2–4 | Không | Mực/QR phải đọc được, thử nắng mưa | [MakerWorld](https://makerworld.com/en/3d-models), ý tưởng nhãn cây; thiết kế mới |
| 2 ★ | Đế QR để bàn thay nội dung bằng tham số | Quán/cửa hàng | Tái dùng cho nhiều khổ QR | Quán cà phê đặt tên/logo có quyền | 2–4 | Không | Logo do khách xác nhận; cần ổn định | [Printables](https://www.printables.com/model), thiết kế mới |
| 3 ★ | Bookmark/nametag chủ đề hoa-cà phê Đà Lạt | Quà địa phương | Nhẹ, dễ in, dễ biến thể | Quà lưu niệm/đặt tên | 2–5 | Không | Không dùng hình/logo bên thứ ba | [Cổng du lịch Đà Lạt](https://dalat.vn/), tham khảo chủ đề |
| 4 ★ | Kẹp dây bàn học có khắc tên | Organizer/trường học | Tiện ích phổ thông, tham số hóa | Quà lớp/đơn trường | 2–4 | Không | Khe/kẹp cần thử độ bền; chi tiết nhỏ | [MakerWorld](https://makerworld.com/en/3d-models), thiết kế mới |
| 5 ★ | Thước góc/hộp bài học bánh răng STEAM | Giáo dục STEAM | Có hướng dẫn hoạt động lớp | Bộ học cụ cho trường/Open Lab | 4–8 | Không | Chi tiết nhỏ, không phải đồ chơi chứng nhận | [Printables Education](https://www.printables.com/education), thiết kế mới |
| 6 | Kẹp túi cà phê có tag tên nông trại | Quà/cửa hàng | Biến thể chữ và độ dài | Quán/roastery/đóng quà | 2–5 | Không | Không khẳng định food-safe; lực kẹp thử nghiệm | [Cults3D](https://cults3d.com/en/3d-printing), tham khảo category |
| 7 | Kệ menu gập/đế danh thiếp modular | Quán/cửa hàng | File hữu ích, có profile | Quán, homestay, shop | 4–8 | Không | Kích thước menu phải lấy từ khách | [MakerWorld](https://makerworld.com/en/3d-models), thiết kế mới |
| 8 | Móc khóa địa hình/hoa bản quyền STLab | Quà địa phương | Dễ cá nhân hóa, ít vật liệu | Quà khách du lịch | 3–6 | Có nếu phối màu; một màu không cần | Tránh biểu trưng/nhân vật có quyền | [Cổng du lịch Đà Lạt](https://dalat.vn/), gợi ý chủ đề |
| 9 | Khay ươm mô-đun và marker đánh số | Nông nghiệp | Chia sẻ bài học trồng cây | Nông trại/vườn ươm | 5–9 | Không | Kích thước cây/đất phải thử thực tế | [MakerWorld](https://makerworld.com/en/3d-models), thiết kế mới |
| 10 | Giá đỡ điện thoại gập cho bàn học | Phụ kiện máy tính | Tiện ích phổ thông | Quà học sinh/quán | 3–6 | Không | Không đảm bảo mọi máy/ốp vừa | [Printables](https://www.printables.com/model), thiết kế mới |
| 11 | Hộp cảm biến ESP32 có nắp tham số | Vỏ điện tử | Có thể công bố file và sơ đồ lắp | Dự án STEM/nông trại | 5–10 | Không | Không thay vỏ điện an toàn/chống nước | [MakerWorld](https://makerworld.com/en/3d-models), dùng kích thước do STLab đo |
| 12 | Kẹp giữ thẻ tên/chậu hoa | Nông nghiệp/hoa | Mẫu nhỏ, dễ tùy biến | Vườn hoa/nhà kính | 2–5 | Không | UV/nhiệt/độ bền cần thử | [Cổng du lịch Đà Lạt](https://dalat.vn/), thiết kế mới |
| 13 | Cơ cấu fidget/print-in-place nguyên bản | Đồ chơi/fidget | Dễ thu hút lượt thử | Bán tại Open Lab/quà nhỏ | 5–10 | Không | Kẹt khớp, cạnh, chi tiết nhỏ; không nhắm trẻ nhỏ nếu chưa đánh giá | [MakerWorld](https://makerworld.com/en/3d-models), xu hướng định tính |
| 14 | Bộ phụ kiện robot giữ cảm biến (sau khi đo) | CyberBrick/robot | Hữu ích cho maker/giáo dục | Bộ kit STEAM | 5–10 | Không | Không suy đoán kích thước giao diện; thử fit trước | [fit-library](../../tools/model-study/fit-library), chỉ dùng số đã kiểm chứng |
| 15 | Giá dụng cụ/nozzle cho bàn máy in | Phụ kiện máy in 3D | Tệp tiện ích cho maker | Bán trong Open Lab/cộng đồng | 3–6 | Có nếu mã màu; đơn sắc không cần | Tránh chạm vùng nóng/chuyển động | [MakerWorld](https://makerworld.com/en/3d-models), thiết kế mới |

★ **Năm mẫu nên làm trước để Tuan chọn:** nhãn cây tham số, đế QR, bookmark/nametag địa phương, kẹp dây có tên, thước góc/kit bánh răng STEAM. Mục tiêu sơ bộ: một màu, không support trong STL, lát cắt dưới 3 giờ, tạo được biến thể tham số. Chưa có file slice nên khối lượng/thời gian cụ thể đều cần đo trước khi triển khai hoặc báo giá.

### Nguồn đã tra (truy cập 2026-11-02)

- [S1] Bambu Lab A1 – thông số chính thức (256 × 256 × 256 mm, PETG được hỗ trợ): https://bambulab.com/en/a1/tech-specs
- [S2] MakerWorld – [trang model](https://makerworld.com/en/3d-models), [điểm](https://makerworld.com/en/points), [điều khoản](https://makerworld.com/en/legal/terms), [wiki release notes](https://wiki.bambulab.com/en/makerworld/release-note/makerworld-release-notes). Một số URL policy bị chặn khi truy cập tự động; đọc trực tiếp lại trước khi đăng.
- [S3] Printables – [thư viện](https://www.printables.com/model), [Club](https://www.printables.com/club), [trợ giúp Prusameters](https://help.prusa3d.com/article/prusameters_1778) (trang trợ giúp trả 404 ở lần tra cứu; không chốt mức quy đổi).
- [S4] Thingiverse – [About](https://www.thingiverse.com/about), [điều khoản thiết kế](https://www.thingiverse.com/terms/designs).
- [S5] Cults3D – [trang chính](https://cults3d.com/), [FAQ](https://cults3d.com/en/pages/faq) (trả 403; phí/commission cần xác nhận).
- [S6] Thangs – [Creator Program](https://thangs.com/creator-program) (trả 403; payout/điều kiện cần xác nhận).
- [S7] Danh mục để quan sát xu hướng: [MakerWorld models](https://makerworld.com/en/3d-models), [Printables models](https://www.printables.com/model), [Thingiverse](https://www.thingiverse.com/), [Cults3D](https://cults3d.com/).
- [S8] An toàn/vật liệu: [Bambu A1 materials](https://bambulab.com/en/a1/tech-specs), [Prusa Knowledge Base – vật liệu](https://help.prusa3d.com/materials). Chưa xác minh chứng nhận tiếp xúc thực phẩm hay ngưỡng nhiệt cho cuộn PETG Basic cụ thể.
- Thị trường: [Shopee search](https://shopee.vn/search?keyword=m%C3%B3c%20kh%C3%B3a%20in%203D), [Facebook Marketplace](https://www.facebook.com/marketplace/search/?query=do%20in%203D), [TikTok Shop](https://www.tiktok.com/shop/search?q=in%203D); nội dung/giá phụ thuộc vị trí, đăng nhập và listing động.
- Pháp lý: [Cơ sở dữ liệu quốc gia về văn bản pháp luật](https://vbpl.vn/), [Cổng văn bản Chính phủ](https://vanban.chinhphu.vn/), [Bộ Công Thương](https://moit.gov.vn/), [online.gov.vn](https://online.gov.vn/), [TCVN](https://tcvn.gov.vn/).

## 9. Bo sung (Codex tra web 2026-11-02)

Codex tra; Claude chưa mở từng link – kiểm lại trước khi dùng. Link shop Shopee (không phải listing) đánh dấu "link shop".

### 9.1 Nền tảng

| Nền tảng / chương trình | Thông tin | Nguồn |
|---|---|---|
| MakerWorld – điểm thưởng | Bảng điểm/lượt tải hiện hành không công bố (TODO). Đổi được gift card/quà shop; tỷ giá điểm thường TODO. | [Bambu Lab blog](https://blog.bambulab.com/makerworld-3d-model-platform/) |
| MakerWorld – Exclusive Model Program | Exclusive Points ≈ 0,066 USD/điểm; rút tiền mặt mỗi 100 USD; có hỗ trợ bản quyền. Điều khoản độc quyền (có phải gỡ ở nơi khác không): TODO. | [Exclusive Model Program](https://blog.bambulab.com/exclusive-model-program-cash-rewards-and-copyright-support/), [Copyright protection](https://blog.bambulab.com/makerworld-launches-creator-copyright-protection-program/) |
| MakerWorld – Boost | Người dùng tích cực nhận tối đa 3 token/tuần để boost; mỗi boost tác giả nhận ≈ gift card 1 USD (theo thông báo gốc, mức hiện tại cần kiểm). | [Boost](https://blog.bambulab.com/boosting-what-matters-rewarding-engineering-and-design-effort/), [Rethinking rewards](https://blog.bambulab.com/rethinking-rewards-makerworld-boost-system/) |
| MakerWorld – Commercial License Membership | Tác giả bán gói thuê bao (3–300 USD/tháng theo thông báo ra mắt) cho người khác quyền in bán; phí nền tảng 10 % + phí thanh toán. | [Commercial License](https://blog.bambulab.com/empowering-our-creators-with-new-commercial-license-membership/) |
| MakerWorld – License | Standard Digital File License cấm người tải dùng thương mại. Tác giả gốc tự in bán mẫu của chính mình: chưa thấy văn bản chính thức (TODO – Tuan đọc điều khoản khi đăng). Ghi chú Claude: tác giả giữ bản quyền thiết kế gốc, license cấp cho người tải nên thường không cản tác giả – nhưng phải xác nhận. | – |
| MakerWorld – Parametric Model Maker (OpenSCAD) | Có trên MakerWorld → đăng mẫu tùy biến được; luật chi tiết TODO. | – |
| Printables – Prusameters | Theo mốc lượt tải: 10/50/100/200 điểm ở 30/100/200/400 lượt tải, cần đủ like. 350 Prusameters = voucher 1 cuộn Prusament PLA/PETG/ASA. | [Prusameters](https://help.prusa3d.com/article/how-do-prusameters-on-printables-work_365065) |
| Printables – Club | Printables lấy 10 % + phí Stripe; mẫu exclusive không tính Prusameters. | [For creators](https://help.prusa3d.com/ja/article/for-creators_497205) |
| Cults3D | Sàn lấy 20 %, tác giả nhận 80 % giá bán ròng. | [VAT rules](https://cults3d.com/en/pages/vat-application-rules) |

### 9.2 Giá bán tham khảo Shopee (giá hiển thị 2026-11-02, có thể đổi)

| Loại | Giá (đ) | Link |
|---|---:|---|
| Móc khóa in tên | 20.000 | https://shopee.vn/M%C3%B3c-Kh%C3%B3a-In-T%C3%AAn-Theo-Y%C3%AAu-C%E1%BA%A7u-Bunny-3D-M%C3%B3c-Kh%C3%B3a-Nh%E1%BB%B1a-In-3D-C%C3%A1-Nh%C3%A2n-H%C3%B3a-Qu%C3%A0-T%E1%BA%B7ng-B%E1%BA%A1n-B%C3%A8-B%C3%A9-C%E1%BA%B7p-%C4%90%C3%B4i-i.1664761907.47268985271 |
| Móc khóa in tên | 25.000–30.000 | https://shopee.vn/M%C3%B3c-kho%C3%A1-in-3D-theo-y%C3%AAu-c%E1%BA%A7u-%28-ghi-t%C3%AAn-gi%C3%BAp-shop-khi-%C4%91%E1%BA%B7t-h%C3%A0ng-nh%C3%A9%29-i.314155488.50661547162 |
| Móc khóa rồng khớp nối | 27.000 | https://shopee.vn/M%C3%B3c-kho%C3%A1-qu%C3%A0-t%E1%BA%B7ng-c%E1%BA%B7p-r%E1%BB%93ng-kh%E1%BB%9Bp-n%E1%BB%91i-in-3D-decor-g%C3%B3c-l%C3%A0m-vi%E1%BB%87c-i.194576644.45906766177 |
| Giá đỡ điện thoại | 54.900 | link shop: https://shopee.vn/toyin3d |
| Giá đỡ điện thoại | 62.100 | link shop: https://shopee.vn/3dluxi1 |
| Giá đỡ điện thoại in theo tên | 150.000 | https://shopee.vn/%F0%9F%93%B1-GI%C3%81-%C4%90%E1%BB%A0-%C4%90I%E1%BB%86N-THO%E1%BA%A0I-IN-3D-THEO-T%C3%8AN-%E2%80%93-CH%E1%BB%88-D%C3%80NH-RI%C3%8ANG-CHO-B%E1%BA%A0N%21-%F0%9F%92%96-i.370394650.41032121438 |
| Bảng tên để bàn | 65.000–70.000 | https://shopee.vn/B%E1%BA%A3ng-T%C3%AAn-In-3D-N%E1%BB%95i-Kh%E1%BB%91i-%C4%90%E1%BB%83-B%C3%A0n-%E2%80%93-Nh%E1%BB%B1a-3D-Cao-C%E1%BA%A5p-T%C3%B9y-Ch%E1%BB%8Dn-Ch%E1%BB%AF-%E2%80%93-Trang-Tr%C3%AD-B%C3%A0n-L%C3%A0m-Vi%E1%BB%87c-Quay-Video-i.1338334787.26693101734 |
| Bảng tên để bàn | 90.000 | https://shopee.vn/B%E1%BA%A3ng-T%C3%AAn-In-3D-Thi%E1%BA%BFt-K%E1%BA%BF-Theo-Y%C3%AAu-C%E1%BA%A7u-Decor-B%C3%A0n-L%C3%A0m-Vi%E1%BB%87c-Phong-C%C3%A1ch-Minimalist-Sang-Tr%E1%BB%8Dng-M%C3%AA-3D--i.205064900.54758015616 |
| Bảng tên để bàn | 100.000–150.000 | https://shopee.vn/B%E1%BA%A3ng-T%C3%AAn-In-3D-Theo-Y%C3%AAu-C%E1%BA%A7u-%E2%80%93-Name-Plate-%C4%90%E1%BB%83-B%C3%A0n-%E2%80%93-Thi%E1%BA%BFt-K%E1%BA%BF-C%C3%A1-Nh%C3%A2n-H%C3%B3a-i.87548493.43728925213 |
| Khay/organizer bàn | 79.000 | link shop: https://shopee.vn/yuri.top1 |
| Khay/organizer bàn | 56.871 | link shop: https://shopee.vn/tb3dstore |
| Rồng khớp nối | 30.000–50.000 | https://shopee.vn/M%C3%B4-h%C3%ACnh-r%E1%BB%93ng-kh%E1%BB%9Bp-n%E1%BB%91i-in-3D-%E2%80%93-R%E1%BB%93ng-u%E1%BB%91n-cong-linh-ho%E1%BA%A1t-trang-tr%C3%AD-b%C3%A0n-l%C3%A0m-vi%E1%BB%87c-i.18157216.50905000298 |
| Rồng khớp nối | 46.000–105.000 | https://shopee.vn/M%C3%B4-H%C3%ACnh-R%E1%BB%93ng-Kh%E1%BB%9Bp-N%E1%BB%91i-In-3D-%E2%80%93-Nh%E1%BB%B1a-PLA-Cao-C%E1%BA%A5p-Thi%E1%BA%BFt-K%E1%BA%BF-X%C6%B0%C6%A1ng-%C4%90%E1%BB%99c-L%E1%BA%A1-Trang-Tr%C3%AD-S%C6%B0u-T%E1%BA%A7m-MHR2-7-i.1629491158.40568430954 |
| Rồng khớp nối | 80.000 | https://shopee.vn/%F0%9F%90%89-SI%C3%8AU-PH%E1%BA%A8M-M%C3%94-H%C3%8CNH-R%E1%BB%92NG-KH%E1%BB%9AP-N%E1%BB%90I-IN-3D-%28ARTICULATED-DRAGON%29-i.883986124.49265320721 |

### 9.3 Nhận xét của Claude

- Đồ phổ thông trên Shopee rẻ (móc khóa 20–30 nghìn, rồng 30–80 nghìn) → cạnh tranh giá khó; lợi thế STLab là đồ cá nhân hóa (bảng tên 65–150 nghìn, giá đỡ in tên 150 nghìn) và đồ ngách địa phương/STEAM.
- So giá bán với giá vốn từ `/quote` trước khi chốt.
- Muốn tiền mặt từ MakerWorld thì cần Exclusive (ràng buộc độc quyền chưa rõ) – nên bắt đầu đăng thường để lấy điểm + uy tín, quyết Exclusive sau.
