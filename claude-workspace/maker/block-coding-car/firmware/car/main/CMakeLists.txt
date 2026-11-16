idf_component_register(
    SRCS "main.c" "prog.c" "stepper.c" "sound.c" "eyes.c" "batt.c" "netcfg.c"
    INCLUDE_DIRS "."
    REQUIRES esp_http_server esp_wifi esp_event esp_netif nvs_flash esp_timer app_update esp_app_format
             esp_driver_gpio esp_driver_i2s esp_driver_uart esp_adc esp_driver_rmt json mdns lwip
    EMBED_FILES "www/index.html.gz"
)
