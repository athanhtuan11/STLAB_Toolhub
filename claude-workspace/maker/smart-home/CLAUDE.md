# smart-home – ESP32 + ESPHome + Home Assistant

## Mục tiêu
TODO: các phòng/thiết bị cần tự động hóa.

## Thành phần
- Thiết bị: ESP32 chạy ESPHome; cấu hình YAML trong `esphome/<thiet-bi>.yaml`.
- Home Assistant: TODO (HAOS / Docker / Supervised?, phiên bản, địa chỉ).
- Bí mật: `esphome/secrets.yaml` (đã có trong .gitignore? TODO), **không** ghi Wi-Fi/API key vào file khác.

## Lệnh
- Kiểm tra cấu hình: `esphome config esphome/<thiet-bi>.yaml`
- Biên dịch: `esphome compile esphome/<thiet-bi>.yaml`
- Flash/OTA: `esphome upload ...` (chỉ chạy khi Tuan đồng ý).

## Skill / agent
- `home-assistant-best-practices` (homeassistant-ai/skills, MIT): ưu tiên trigger/condition
  gốc thay vì template; dùng `entity_id` thay vì `device_id`.
- Agent `iot-engineer`, `embedded-systems`.

## MCP (chưa bật)
- `ha-mcp` v8.7.0 đã ghim trong `community/`. Khi bật: dùng tài khoản HA riêng,
  token để trong biến môi trường, bắt đầu ở chế độ **read-only** (`/readonly`).
- ESPHome MCP: chưa dùng (các repo hiện có quá mới, ít người dùng).
