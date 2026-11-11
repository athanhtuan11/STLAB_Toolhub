# Đưa cô giáo tiếng Anh ra domain qua VPS (Tuan chọn 2026-11-11) – ĐANG CHẠY

`https://engteacher.mamnoncaynho.com` – bo dùng được ở mọi nơi có Wi-Fi. Máy chủ (bridge Gemini Live) **vẫn chạy ở máy
lab**; VPS Tino (180.93.138.55, Ubuntu 24.04, đã có nginx phục vụ `mamnoncaynho.com`) chỉ làm cổng.

```
Bo ESP32 ──https/wss──▶ nginx VPS (site "engteacher", certbot) ──▶ 127.0.0.1:18003 / :18000 trên VPS
                                                                        ▲ đường hầm SSH (máy lab chủ động nối ra cổng 22)
                                             máy lab: deploy/tunnel.ps1 ──▶ bridge 8003 (OTA) / 8000 (WebSocket)
```

- Không mở cổng trên modem. **Máy lab phải bật** thì bo mới dùng được.
- Đường hầm dùng OpenSSH có sẵn trong Windows. frp đã bỏ vì Windows Defender chặn `frpc.exe` (bản cũ ở
  `backup/20261111-frp-to-ssh-tunnel/`, chỉ có trên máy).
- User `engtunnel` trên VPS: không shell, khóa mật khẩu, chỉ được mở `127.0.0.1:18000` và `:18003` (đã thử: `id` bị từ
  chối, mở cổng 2222 bị từ chối). Khóa riêng `~/.ssh/id_ed25519_engtunnel` (khác khóa root `id_ed25519_tino`).
- Khóa bo: OTA chỉ trả token cho bo trong `STLAB_ALLOWED_DEVICES` (bo lạ, thiếu Device-Id → 403); WebSocket sai token →
  đóng 4401. Bật domain mà thiếu token/danh sách thì bridge **không chạy**. Gate: `test_public_access.py`.
- ⚠️ Bridge ghi "CHỈ NGƯỜI LỚN THỬ NỘI BỘ" (điều khoản Gemini API với người < 18 tuổi) – Tuan quyết khi cho bé dùng ở nhà.

## Biến môi trường người dùng trên máy lab (không ghi vào file nào)
| Biến | Giá trị |
|---|---|
| `STLAB_PUBLIC_HOST` | `engteacher.mamnoncaynho.com` |
| `STLAB_TUNNEL_HOST` | `engtunnel@180.93.138.55` |
| `STLAB_ALLOWED_DEVICES` | `e0:8c:fe:64:20:a4` (bo A1S); bo mới: thêm, cách dấu phẩy |
| `STLAB_DEVICE_TOKEN` | 43 ký tự ngẫu nhiên (đã tạo, không in ra) |

`run-live.ps1` tự bật `deploy/tunnel.ps1` (rớt mạng tự nối lại sau 5 s, log `runtime/tunnel.log`).

## Đã kiểm (2026-11-11)
| Kiểm | Kết quả |
|---|---|
| `https://engteacher.mamnoncaynho.com/` | 404 (đúng – chỉ mở 2 đường dẫn), chứng chỉ hạn 2027-02-09, certbot tự gia hạn |
| OTA bo đúng | JSON `wss://engteacher.mamnoncaynho.com/xiaozhi/v1/` + token |
| OTA bo lạ / thiếu Device-Id | 403 / 403 |
| `http://` | 301 → `https://` |
| WebSocket sai token / đúng token | đóng 4401 / nhận `hello` |
| `https://mamnoncaynho.com/` | 200 (web cũ không ảnh hưởng) |

Chưa kiểm: bo thật nói chuyện qua domain, độ trễ qua 4G.

## Bo
- Bo đang nạp `ota_url` LAN (192.168.1.56) vẫn chạy: OTA trả `wss://` domain → đi vòng qua VPS cả khi ở lab.
- Dùng ngoài lab: cắm COM5 (Tuan đồng ý) →
  `python ..\firmware\xiaozhi-a1s\wifi-nvs.py --port COM5 --ota-url https://engteacher.mamnoncaynho.com/xiaozhi/ota/ --ssid <Wi-Fi nơi dùng>`.

## Cài lại VPS từ đầu
Chép `setup-vps.sh` + `nginx-engteacher.conf` (đuôi dòng LF) lên VPS, chạy bằng root:
`TUNNEL_PUBKEY="<nội dung id_ed25519_engtunnel.pub>" bash setup-vps.sh`. Sao lưu nginx tự động ở `/root/backup/`.

## Gỡ
- Máy lab: xóa `STLAB_PUBLIC_HOST` + `STLAB_TUNNEL_HOST` → về chế độ LAN; nạp lại bo `wifi-nvs.py --server 192.168.1.56`.
- VPS: `rm /etc/nginx/sites-enabled/engteacher && systemctl reload nginx`; `userdel -r engtunnel`.
