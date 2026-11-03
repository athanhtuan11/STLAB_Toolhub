idf_component_register(
    SRCS "probe_main.c" "wifi_nha.c"
    INCLUDE_DIRS "."
    REQUIRES esp_http_server esp_wifi esp_event esp_netif nvs_flash esp_timer esp_psram spi_flash esp_driver_i2c esp_driver_tsens esp_driver_uart mdns
    EMBED_TXTFILES "index.html"
)
