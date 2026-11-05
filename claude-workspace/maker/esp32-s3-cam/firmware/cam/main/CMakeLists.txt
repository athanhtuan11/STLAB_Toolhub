idf_component_register(
    SRCS "cam_main.c" "wifi_nha.c"
    INCLUDE_DIRS "."
    REQUIRES esp_http_server esp_wifi esp_event esp_netif nvs_flash esp_timer esp_psram esp_driver_tsens esp_driver_uart esp_driver_gpio esp_driver_sdmmc sdmmc fatfs vfs app_update lwip mdns esp_pm
    EMBED_TXTFILES "index.html"
)
