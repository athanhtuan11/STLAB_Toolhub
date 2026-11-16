// Chay thu tren may tinh: doc file JSON (argv[1]), bung chuong trinh, in dung 1 dong JSON ket qua.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "prog.h"

static char *read_file(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (f == NULL) {
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = (char *)malloc((size_t)n + 1);
    if (buf == NULL) {
        fclose(f);
        return NULL;
    }
    size_t got = fread(buf, 1, (size_t)n, f);
    buf[got] = '\0';
    fclose(f);
    return buf;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "dung: run_golden <file.json>\n");
        return 2;
    }
    char *text = read_file(argv[1]);
    if (text == NULL) {
        fprintf(stderr, "khong doc duoc %s\n", argv[1]);
        return 2;
    }
    prog_step_t steps[PROG_MAX_STEPS];
    const char *err = NULL;
    int n = prog_expand(text, steps, PROG_MAX_STEPS, &err);
    if (n < 0) {
        printf("{\"ok\":false,\"code\":\"%s\"}\n", err != NULL ? err : "bad_json");
    } else {
        printf("{\"ok\":true,\"steps\":[");
        for (int i = 0; i < n; i++) {
            printf("%s[%d,\"%s\",%d]", i > 0 ? "," : "", steps[i].id, prog_op_name(steps[i].op), steps[i].arg);
        }
        printf("]}\n");
    }
    free(text);
    return 0;
}
