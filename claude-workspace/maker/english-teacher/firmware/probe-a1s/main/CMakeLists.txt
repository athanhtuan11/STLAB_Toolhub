idf_component_register(
    SRCS "probe_a1s_main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_driver_i2c esp_driver_i2s esp_driver_gpio esp_driver_uart esp_psram spi_flash esp_hw_support heap esp_timer
)
