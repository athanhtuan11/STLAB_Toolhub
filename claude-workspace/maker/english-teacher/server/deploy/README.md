# Đưa cô giáo tiếng Anh ra domain qua VPS (Tuan chọn 2026-11-11)

Bo dùng được ở mọi nơi có Wi-Fi. Máy chủ (bridge Gemini Live) **vẫn chạy ở máy lab**; VPS Tino chỉ làm cổng.

```
Bo ESP32 ──https/wss──▶ teacher.<domain> (VPS: Caddy 443) ──▶ frps 127.0.0.1:18003/18000
                                                                   ▲ đường hầm TLS (máy lab chủ động nối ra, cổng 7000)
                                              máy lab: frpc ──▶ bridge 8003 (OTA) / 8000 (WebSocket)
```

- Không mở cổng trên modem. Máy lab phải bật thì bo mới dùng được.
- Khóa: OTA chỉ trả token cho bo trong `STLAB_ALLOWED_DEVICES`; WebSocket cần đúng token + đúng bo. Bật domain mà thiếu
  token/danh sách thì bridge **không chạy** (`check_public_config`, gate `test_public_access.py`).
- ⚠️ Bridge ghi "CHỈ NGƯỜI LỚN THỬ NỘI BỘ" (điều khoản Gemini API với người < 18 tuổi). Đưa ra internet cho bé dùng ở nhà:
  Tuan quyết (`TODO` đọc lại điều khoản).

## Biến môi trường (không ghi vào file nào)
| Biến | Ở đâu | Ví dụ / ghi chú |
|---|---|---|
| `STLAB_PUBLIC_HOST` | máy lab (biến người dùng) | `teacher.<domain>` |
| `STLAB_DEVICE_TOKEN` | máy lab | ≥ 24 ký tự ngẫu nhiên |
| `STLAB_ALLOWED_DEVICES` | máy lab | `e0:8c:fe:64:20:a4` (bo A1S), thêm bo mới cách dấu phẩy |
| `FRP_SERVER_ADDR` | máy lab | IP VPS |
| `FRP_AUTH_TOKEN` | máy lab + VPS (`/etc/frp/frps.env`) | ≥ 24 ký tự ngẫu nhiên, khác token bo |

Tạo chuỗi ngẫu nhiên: `python -c "import secrets;print(secrets.token_urlsafe(32))"`.

## Các bước
1. **Tuan – DNS:** tại nơi đăng ký domain, thêm bản ghi `A`: `teacher` → IP VPS (TTL thấp). Không cần Cloudflare.
2. **Tuan – SSH:** thêm khóa công khai `~/.ssh/id_ed25519_tino.pub` của máy lab vào VPS (`/root/.ssh/authorized_keys` hoặc trang Tino).
3. **Claude – VPS:** chép `Caddyfile`, `frps.toml`, `setup-vps.sh` lên VPS rồi chạy
   `PUBLIC_HOST=... FRP_VERSION=... FRP_AUTH_TOKEN=... bash setup-vps.sh`. Kiểm `https://teacher.<domain>/` → 404 (Caddy + chứng chỉ OK).
4. **Máy lab:** `.\deploy\get-frpc.ps1 -Version <cùng bản frps>`; đặt 5 biến môi trường ở bảng trên; khởi động lại máy chủ
   (`run-live.ps1` tự bật frpc). Kiểm: `curl -H "Device-Id: e0:8c:fe:64:20:a4" https://teacher.<domain>/xiaozhi/ota/` → JSON có `wss://`.
5. **Bo (cắm COM5, Tuan đồng ý nạp):** `python ..\firmware\xiaozhi-a1s\wifi-nvs.py --port COM5 --ota-url https://teacher.<domain>/xiaozhi/ota/`
   (Wi-Fi nơi dùng: thêm `--ssid`). Không build lại firmware.
6. **Thử:** tắt Wi-Fi lab, cho bo bắt điểm phát 4G điện thoại → chạm KEY4 nói thử. Ghi độ trễ vào README dự án.

## Gỡ
- Máy lab: xóa `FRP_SERVER_ADDR` + `STLAB_PUBLIC_HOST` → về chế độ LAN; nạp lại bo `wifi-nvs.py --server 192.168.1.56`.
- VPS: `systemctl disable --now frps caddy`.
