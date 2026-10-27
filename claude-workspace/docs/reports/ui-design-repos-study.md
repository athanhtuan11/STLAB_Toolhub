# Nghiên cứu 12 repo thiết kế UI cho STLAB Toolhub

Phạm vi: đọc mã/tài liệu đã clone; Toolhub hiện là Flask + HTML/CSS/JS theo `studio/toolhub/templates/base.html` và `studio/toolhub/static/style.css`. Không chạy/cài repo nghiên cứu.

## 1. Tong quan 12 repo

| Repo | Loại | Cần framework gì (React? Node?) | Flask + HTML? | File chính dẫn chứng |
|---|---|---|---|---|
| `nextlevelbuilder-ui-ux-pro-max-skill` | Skill cho agent + dữ liệu tra cứu | Python 3 cho search; CLI riêng dùng Node | Có: đọc CSV/quy tắc, không cần tích hợp UI | `community/nextlevelbuilder-ui-ux-pro-max-skill/CLAUDE.md`; `community/nextlevelbuilder-ui-ux-pro-max-skill/src/ui-ux-pro-max/data/ux-guidelines.csv` |
| `voltagent-awesome-design-md` | Bộ DESIGN.md | Không yêu cầu framework | Có: lấy cấu trúc/ý tưởng, không lấy nguyên palette thương hiệu | `community/voltagent-awesome-design-md/README.md`; `community/voltagent-awesome-design-md/design-md/vercel/DESIGN.md` |
| `nexu-io-open-design` | App desktop, kèm template/skill | App dùng Node/TS; các template khác nhau | Một số template xuất HTML; app không phải dependency Flask | `community/nexu-io-open-design/package.json`; `community/nexu-io-open-design/design-templates/wireframe-sketch/SKILL.md` |
| `leonxlnx-taste-skill` | Skill cho agent, kèm lint script | Node để chạy lint; không cần React với hướng dẫn CSS/web | Có: quy tắc thẩm mỹ áp vào HTML/CSS | `community/leonxlnx-taste-skill/skills/taste-skill/SKILL.md`; `community/leonxlnx-taste-skill/skills/taste-skill/scripts/lint.mjs` |
| `pbakaus-impeccable` | Skill/CLI kiểm và chỉnh UI | CLI có engine và tooling riêng; không cần React để dùng nguyên tắc | Có: dùng checklist/rule khi review HTML/CSS | `community/pbakaus-impeccable/README.md`; `community/pbakaus-impeccable/DESIGN.md`; `community/pbakaus-impeccable/crates/core/src/checks/rules.rs` |
| `davidhdev-react-bits` | Thư viện component/hiệu ứng | React và toolchain JS | Không dùng trực tiếp nếu không chuyển đổi; ý tưởng hiệu ứng có thể tự viết | `community/davidhdev-react-bits/package.json`; `community/davidhdev-react-bits/LICENSE.md` |
| `emilkowalski-skills` | Bộ skill về thiết kế/animation | Nhiều skill hướng React; nguyên tắc motion độc lập framework | Có: áp dụng CSS transitions và reduced-motion | `community/emilkowalski-skills/skills/review-animations/STANDARDS.md`; `community/emilkowalski-skills/skills/animate/RECIPES.md` |
| `nutlope-hallmark` | Skill + linter chống giao diện rập khuôn | Node; linter đọc HTML/CSS, một số chế độ render dùng browser | Có: kiểm HTML/CSS; cần Node nếu chạy script | `community/nutlope-hallmark/skills/hallmark/SKILL.md`; `community/nutlope-hallmark/skills/hallmark/scripts/sloplint.mjs` |
| `google-labs-code-design-md` | Định dạng DESIGN.md và CLI | Định dạng không cần framework; CLI dùng Node/Bun | Có: cấu trúc tài liệu/tokens dùng độc lập | `community/google-labs-code-design-md/docs/spec.md`; `community/google-labs-code-design-md/examples/atmospheric-glass/DESIGN.md` |
| `greensock-gsap-skills` | Skill và thư viện animation GSAP | JS; ví dụ vanilla, Vue, React | Có với vanilla JS; ví dụ nạp GSAP từ CDN, cần mạng | `community/greensock-gsap-skills/examples/vanilla/main.js`; `community/greensock-gsap-skills/skills/gsap-scrolltrigger/SKILL.md` |
| `oso95-scroll-world` | Skill tạo landing page scroll-cinematic | Vanilla JS được; pipeline cần CLI/dịch vụ tạo ảnh/video bên ngoài | Kỹ thuật scrub engine độc lập framework; pipeline nặng, không hợp mặc định | `community/oso95-scroll-world/skills/scroll-world/SKILL.md`; `community/oso95-scroll-world/skills/scroll-world/references/scrub-engine.js` |
| `davidhdev-canvas-ui` | Thư viện hiệu ứng canvas | Nhiều adapter (React/Vue/Svelte/Solid/vanilla); một số hiệu ứng WebGPU | Có chọn lọc qua Vanilla, cần đánh giá tải và fallback | `community/davidhdev-canvas-ui/src/lib/VHS/VHSVanilla.ts`; `community/davidhdev-canvas-ui/src/lib/Ripple/RippleVanilla.ts`; `community/davidhdev-canvas-ui/LICENSE.md` |

## 2. DESIGN.md

`community/google-labs-code-design-md/docs/spec.md` quy định prose Markdown đi cùng token YAML, có thể ở front matter hoặc khối YAML; schema gồm `colors`, `typography`, `rounded`, `spacing`, `components` và tham chiếu token. Mẫu `community/google-labs-code-design-md/examples/atmospheric-glass/DESIGN.md` minh họa màu bề mặt/trạng thái, cỡ chữ + line-height/letter-spacing, bo góc, spacing và token component.

Các mẫu trong `community/voltagent-awesome-design-md/design-md/vercel/DESIGN.md` bổ sung cách đặt tên vai trò màu, nhiều mức chữ, màu trạng thái, trạng thái tương tác và hướng dẫn bố cục. Đây là mẫu thương hiệu cụ thể; không sao chép nguyên màu/kiểu Vercel.

`studio/design/DESIGN.md` đã có bối cảnh người dùng, palette sáng/tối, font và trọng số, nguyên tắc, checklist tương phản/responsive/focus, cách dùng từng nơi. `studio/design/tokens.json` đã có `light`, `dark`, `status`, `stages`, `font`, `radius`, `esp32.touch_min_px`.

Thiếu hoặc chưa chuẩn hóa so với các mẫu: thang `spacing`; thang typography có vai trò kèm size/line-height/letter-spacing; bảng token component theo vai trò (nút, input, focus, trạng thái); mô tả trạng thái hover/disabled/loading/error của component. `tokens.json` chưa có các nhóm token đó. Đây là thiếu mục mô tả/nhóm token, không phải yêu cầu tự đặt số; nếu bổ sung giá trị thì chủ dự án cần định nghĩa.

## 3. Kiem giao dien

- `community/pbakaus-impeccable/crates/core/src/checks/rules.rs` và `community/pbakaus-impeccable/crates/core/src/checks/css_scan.rs`: kiểm các dấu hiệu gradient/halo/glow, shadow quá rộng, cấu trúc lặp và chữ trang trí. Review Toolhub theo hướng có lý do cho mỗi trang trí; giữ màu trong `tokens.json` và chỉ dùng biến CSS.
- `community/leonxlnx-taste-skill/skills/taste-skill/scripts/lib/rules.mjs`: rule `gradient`, `gradient-text`, `shadow`, `text-shadow`, `mixed-font-headline`, `ai-purple`. Dùng để rà gradient trang trí, bóng trên thẻ tĩnh và đổi font giữa tiêu đề; ngoại lệ chỉ khi có chủ đích sản phẩm.
- `community/nutlope-hallmark/skills/hallmark/scripts/sloplint.mjs`: `sloplint` có kiểm gradient tím-xanh/hồng, glow, shadow, lặp hover lift, literal màu/font ngoài token và hierarchy. Với Toolhub, kiểm inline HTML/CSS và xem cảnh báo theo ngữ cảnh, không biến mọi cảnh báo thành luật cứng.
- `community/nextlevelbuilder-ui-ux-pro-max-skill/src/ui-ux-pro-max/data/ux-guidelines.csv`: `Excessive Motion`, `Reduced Motion`, `Hover vs Tap`, `Color Contrast`, `Horizontal Scroll`, `Touch Friendly`, `Focus Appearance`. Hợp để review trang Flask: không phụ thuộc hover, có focus, responsive, không tràn; đối chiếu ngưỡng với DESIGN hiện hành thay vì nhập lại số mâu thuẫn.

## 4. Hieu ung va component

- `community/davidhdev-react-bits/LICENSE.md` ghi MIT + Commons Clause; thư viện chủ yếu là component React/TSX. Không chép component vào Flask; chỉ học ý tưởng tương tác và tự viết CSS/JS nếu cần.
- `community/davidhdev-canvas-ui/LICENSE.md` cũng ghi MIT + Commons Clause. Có bản `*Vanilla.ts` và nhiều adapter, ví dụ `community/davidhdev-canvas-ui/src/lib/VHS/VHSVanilla.ts`; vanilla khả dụng về kỹ thuật, nhưng hiệu ứng canvas/WebGPU có chi phí và cần fallback. Chưa có nhu cầu cụ thể cho dashboard Toolhub.
- `community/greensock-gsap-skills/examples/vanilla/main.js` cho thấy GSAP + ScrollTrigger thuần JS; `community/greensock-gsap-skills/skills/gsap-react/SKILL.md` dành riêng tích hợp React. Vanilla cần tải GSAP qua URL CDN trong ví dụ, nên không hợp môi trường offline nếu chưa vendoring được phép.
- `community/oso95-scroll-world/skills/scroll-world/references/scrub-engine.js` là vanilla, framework-agnostic; nhưng `community/oso95-scroll-world/skills/scroll-world/SKILL.md` yêu cầu pipeline Higgsfield/Monid, ffmpeg và sinh media có chi phí. Không phù hợp Toolhub vận hành nhẹ.
- `community/emilkowalski-skills/skills/review-animations/STANDARDS.md` là quy tắc độc lập framework: motion phục vụ trạng thái/feedback, tránh animation cho thao tác phím lặp liên tục, tôn trọng khả năng ngắt transition. Áp dụng CSS thuần; các recipe React riêng không cần đưa vào dự án.

## 5. An toan

- `community/nextlevelbuilder-ui-ux-pro-max-skill/CLAUDE.md` mô tả lệnh `python3 .../search.py`; CLI npm và các script refresh có thể dùng mạng/cài dependency. Chỉ đọc CSV/Markdown là đủ cho nghiên cứu này; không chạy lệnh.
- `community/leonxlnx-taste-skill/skills/taste-skill/SKILL.md` gọi các script lint/scene trong workflow; `community/leonxlnx-taste-skill/install.sh` là script cài đặt. Không chạy installer/lint trong tác vụ chỉ đọc.
- `community/nutlope-hallmark/skills/hallmark/SKILL.md` hướng dẫn chạy `sloplint`; `community/nutlope-hallmark/skills/hallmark/scripts/install-hook.mjs` và `community/nutlope-hallmark/skills/hallmark/scripts/lint-hook.mjs` có cơ chế hook. Chỉ xem mã, không cài hook.
- `community/pbakaus-impeccable/README.md` mô tả CLI/plugin; có thể có bước cài/tích hợp vào agent. Repo chứa engine Rust và script tooling; không cần chạy để lấy checklist.
- `community/google-labs-code-design-md/package.json` và `community/google-labs-code-design-md/packages/cli/package.json` khai báo tool Node; không cần cài CLI để tham khảo format.
- `community/greensock-gsap-skills/examples/vanilla/main.js` import GSAP/ScrollTrigger từ `https://cdn.jsdelivr.net`; chạy ví dụ gọi mạng. Tài liệu `community/greensock-gsap-skills/README.md` có ví dụ npx.
- `community/oso95-scroll-world/skills/scroll-world/SKILL.md` chạy kiểm tra CLI Monid/Higgsfield, số dư/tài khoản, ffmpeg; tạo ảnh/video gọi dịch vụ ngoài và có thể tính phí. Không chạy. Đây là pipeline cần chú ý nhất về mạng, credentials và chi phí.
- `community/nexu-io-open-design/design-templates/wireframe-sketch/SKILL.md` sinh HTML và nêu dùng Google Fonts; app có tool server tại `community/nexu-io-open-design/tools/serve/package.json`. Chỉ template có thể tạo đầu ra; không khởi động app/tool server trong nghiên cứu.
- `community/davidhdev-react-bits/package.json` và `community/davidhdev-canvas-ui/package.json` là project JS cài dependency; không chạy npm. Không thấy bằng chứng từ các file đã đọc về hook tự chạy của hai thư viện này.

## 6. Ap dung cho Toolhub

1. Bổ sung vào `studio/design/DESIGN.md` mục vai trò component và trạng thái tương tác; lấy schema `components` từ `community/google-labs-code-design-md/docs/spec.md`. Công sức: nhỏ; giá trị token mới để TODO chủ dự án quyết định.
2. Ghi rõ thang typography và spacing hiện dùng sau khi thống nhất; tham khảo cấu trúc `community/voltagent-awesome-design-md/design-md/vercel/DESIGN.md`, không chép giá trị thương hiệu. Công sức: vừa.
3. Duy trì nguồn màu duy nhất tại `studio/design/tokens.json`; dùng quy tắc literal màu/token từ `community/nutlope-hallmark/skills/hallmark/scripts/sloplint.mjs` làm checklist review thủ công trước. Công sức: nhỏ.
4. Thêm checklist chống gradient/trang trí vô cớ, shadow thẻ tĩnh và tiêu đề đổi font giữa dòng từ `community/leonxlnx-taste-skill/skills/taste-skill/scripts/lib/rules.mjs`. Công sức: nhỏ.
5. Rà responsive, focus nhìn thấy, thao tác không lệ thuộc hover, reduced motion theo `community/nextlevelbuilder-ui-ux-pro-max-skill/src/ui-ux-pro-max/data/ux-guidelines.csv`; giữ checklist hiện hành tại `studio/design/DESIGN.md`. Công sức: nhỏ.
6. Với feedback nhỏ, dùng CSS transition và nguyên tắc tại `community/emilkowalski-skills/skills/review-animations/STANDARDS.md`; không thêm thư viện animation/build. Công sức: nhỏ.
7. Chỉ khi có nhu cầu hiệu ứng canvas cụ thể, thử nghiệm độc lập bản vanilla và kiểm tra license MIT + Commons Clause ở `community/davidhdev-canvas-ui/LICENSE.md`; chưa đưa vào dashboard mặc định. Công sức: lớn.
8. Không đưa pipeline `community/oso95-scroll-world/skills/scroll-world/SKILL.md`, component React `community/davidhdev-react-bits/package.json` hay GSAP CDN `community/greensock-gsap-skills/examples/vanilla/main.js` vào Toolhub mặc định vì thêm dịch vụ/mạng/dependency hoặc framework.
