idf_component_register(
    SRCS "guitar_main.c" "umi_proto.c" "dsp.c"
    INCLUDE_DIRS "."
    REQUIRES bt nvs_flash esp_driver_i2c esp_driver_i2s esp_driver_gpio esp_driver_uart esp_timer
)
