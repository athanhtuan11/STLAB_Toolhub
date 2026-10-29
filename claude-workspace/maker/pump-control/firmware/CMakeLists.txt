# Firmware may bom: ESP32-WROOM-32D + ESP RainMaker (ESP-IDF 5.5)
cmake_minimum_required(VERSION 3.16)
# Phien ban firmware: TANG moi lan cap nhat OTA (RainMaker tu choi ban trung phien ban) - ota.ps1 doc so nay
set(PROJECT_VER "1.2.0")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(pump_control)
