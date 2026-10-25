#include "ota_pull.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cJSON.h"
#include "esp_app_desc.h"
#include "esp_crt_bundle.h"
#include "esp_http_client.h"
#include "esp_https_ota.h"
#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Noi Tuan dang ban moi (release.ps1 ghi file nay). raw.githubusercontent cache ~5 phut sau khi push.
#define MANIFEST_URL "https://raw.githubusercontent.com/athanhtuan11/STLAB_Toolhub/main/" \
                     "claude-workspace/maker/pump-control/firmware/releases/manifest.json"
#define MANIFEST_MAX 1024

static const char *TAG = "ota_pull";

static ota_pull_status_cb_t s_cb;
static volatile bool s_busy;

typedef struct {
    char version[32];
    char url[256];
    char notes[96];
} manifest_t;

static void report(const char *fmt, ...)
{
    char buf[128];
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    ESP_LOGI(TAG, "%s", buf);
    if (s_cb) {
        s_cb(buf);
    }
}

// "1.2.10" -> so sanh tung so; tra >0 neu a moi hon b
static int ver_cmp(const char *a, const char *b)
{
    int a1 = 0, a2 = 0, a3 = 0, b1 = 0, b2 = 0, b3 = 0;
    sscanf(a, "%d.%d.%d", &a1, &a2, &a3);
    sscanf(b, "%d.%d.%d", &b1, &b2, &b3);
    if (a1 != b1) return a1 - b1;
    if (a2 != b2) return a2 - b2;
    return a3 - b3;
}

static esp_err_t fetch_manifest(manifest_t *m)
{
    esp_http_client_config_t cfg = {
        .url = MANIFEST_URL,
        .crt_bundle_attach = esp_crt_bundle_attach,
        .timeout_ms = 10000,
    };
    esp_http_client_handle_t c = esp_http_client_init(&cfg);
    esp_err_t err = esp_http_client_open(c, 0);
    char *body = calloc(1, MANIFEST_MAX + 1);
    int n = 0;
    if (err == ESP_OK && body) {
        esp_http_client_fetch_headers(c);
        int status = esp_http_client_get_status_code(c);
        n = esp_http_client_read_response(c, body, MANIFEST_MAX);
        if (status != 200 || n <= 0) {
            ESP_LOGW(TAG, "manifest HTTP %d, %d byte", status, n);
            err = ESP_FAIL;
        }
    }
    esp_http_client_close(c);
    esp_http_client_cleanup(c);
    if (err == ESP_OK) {
        cJSON *j = cJSON_Parse(body);
        const cJSON *v = cJSON_GetObjectItem(j, "version");
        const cJSON *u = cJSON_GetObjectItem(j, "url");
        const cJSON *t = cJSON_GetObjectItem(j, "notes");
        if (cJSON_IsString(v) && cJSON_IsString(u)) {
            strlcpy(m->version, v->valuestring, sizeof(m->version));
            strlcpy(m->url, u->valuestring, sizeof(m->url));
            strlcpy(m->notes, cJSON_IsString(t) ? t->valuestring : "", sizeof(m->notes));
        } else {
            err = ESP_ERR_INVALID_RESPONSE;
        }
        cJSON_Delete(j);
    }
    free(body);
    return err;
}

static void ota_task(void *arg)
{
    bool install = (bool)(intptr_t)arg;
    manifest_t m = {0};
    const char *cur = ota_pull_current_version();
    if (fetch_manifest(&m) != ESP_OK) {
        report("Khong kiem duoc ban moi (mang?) - dang dung %s", cur);
    } else if (ver_cmp(m.version, cur) <= 0) {
        report("Da la ban moi nhat (%s)", cur);
    } else if (!install) {
        report("Co ban %s: %s - bam Cap nhat", m.version, m.notes);
    } else {
        report("Dang cap nhat len %s... (khoang 1 phut, khong rut dien)", m.version);
        esp_http_client_config_t http = {
            .url = m.url,
            .crt_bundle_attach = esp_crt_bundle_attach,
            .timeout_ms = 30000,
            .keep_alive_enable = true,
        };
        esp_https_ota_config_t ota = {.http_config = &http};
        esp_err_t err = esp_https_ota(&ota);
        if (err == ESP_OK) {
            report("Da tai %s - khoi dong lai", m.version);
            vTaskDelay(pdMS_TO_TICKS(3000));  // cho kip bao len app
            esp_restart();
        }
        report("Cap nhat LOI (%s) - van chay %s", esp_err_to_name(err), cur);
    }
    s_busy = false;
    vTaskDelete(NULL);
}

static void start(bool install)
{
    if (s_busy) {
        return;
    }
    s_busy = true;
    if (xTaskCreate(ota_task, "ota_pull", 8192, (void *)(intptr_t)install, 5, NULL) != pdPASS) {
        s_busy = false;
        ESP_LOGE(TAG, "khong tao duoc task");
    }
}

void ota_pull_init(ota_pull_status_cb_t cb)
{
    s_cb = cb;
}

void ota_pull_check_async(void)
{
    start(false);
}

void ota_pull_update_async(void)
{
    start(true);
}

bool ota_pull_busy(void)
{
    return s_busy;
}

const char *ota_pull_current_version(void)
{
    return esp_app_get_description()->version;
}
