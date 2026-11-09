// Ghi AVI MJPEG (RIFF/AVI 1.0 + idx1) - tu viet theo tai lieu Microsoft "AVI RIFF File Reference".
// Chi cac ham thuan (khong IO) de kiem tra duoc ngoai mach (check_v04.py dung ban Python tuong ung).
//
// Bo cuc file (tat ca so nguyen little-endian):
//   0   'RIFF' size 'AVI '
//   12  'LIST' 192 'hdrl'
//   24    'avih' 56 {...}
//   88    'LIST' 116 'strl'
//   100     'strh' 56 {...}
//   164     'strf' 40 {BITMAPINFOHEADER}
//   212 'LIST' size 'movi'            <- 'movi' nam o byte 220
//   224   '00dc' len data [pad]  ...   <- offset trong idx1 tinh tu byte 220 (chunk dau = 4)
//   ...  'idx1' 16*n {'00dc', 0x10, offset, len}
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define AVI_HDR_BYTES 224       // RIFF + hdrl + dau LIST movi (du lieu khung bat dau o day)
#define AVI_MOVI_TAG_POS 220    // vi tri chu 'movi' - goc tinh offset cua idx1
#define AVI_IDX_ENTRY 16
#define AVI_CHUNK_HDR 8

static inline void avi_p16(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
}

static inline void avi_p32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

static inline void avi_tag(uint8_t *p, const char *t)
{
    memcpy(p, t, 4);
}

// Dung 224 byte dau file. chunk_bytes = tong (8 + len + dem chan) cua cac khung trong movi;
// idx_bytes = 16 * so khung. Goi voi (frames = 0, chunk_bytes = 0, idx_bytes = 0) de giu cho luc mo file.
static inline void avi_build_header(uint8_t *h, uint32_t w, uint32_t ht, uint32_t fps_milli, uint32_t frames,
                                    uint32_t max_chunk, uint32_t chunk_bytes, uint32_t idx_bytes)
{
    if (fps_milli == 0) {
        fps_milli = 1000;
    }
    memset(h, 0, AVI_HDR_BYTES);
    avi_tag(h + 0, "RIFF");
    avi_p32(h + 4, 224 + chunk_bytes + idx_bytes);  // = tong file - 8
    avi_tag(h + 8, "AVI ");
    avi_tag(h + 12, "LIST");
    avi_p32(h + 16, 192);
    avi_tag(h + 20, "hdrl");
    // avih
    avi_tag(h + 24, "avih");
    avi_p32(h + 28, 56);
    avi_p32(h + 32, (uint32_t)(1000000000ULL / fps_milli));  // dwMicroSecPerFrame
    avi_p32(h + 36, max_chunk * (fps_milli / 1000 + 1));      // dwMaxBytesPerSec (uoc luong tren)
    avi_p32(h + 40, 0);                                       // dwPaddingGranularity
    avi_p32(h + 44, 0x10);                                    // AVIF_HASINDEX
    avi_p32(h + 48, frames);                                  // dwTotalFrames
    avi_p32(h + 52, 0);                                       // dwInitialFrames
    avi_p32(h + 56, 1);                                       // dwStreams
    avi_p32(h + 60, max_chunk);                               // dwSuggestedBufferSize
    avi_p32(h + 64, w);
    avi_p32(h + 68, ht);
    // dwReserved[4] = 0 (h + 72..87)
    // strl
    avi_tag(h + 88, "LIST");
    avi_p32(h + 92, 116);
    avi_tag(h + 96, "strl");
    avi_tag(h + 100, "strh");
    avi_p32(h + 104, 56);
    avi_tag(h + 108, "vids");
    avi_tag(h + 112, "MJPG");
    avi_p32(h + 116, 0);          // dwFlags
    avi_p16(h + 120, 0);          // wPriority
    avi_p16(h + 122, 0);          // wLanguage
    avi_p32(h + 124, 0);          // dwInitialFrames
    avi_p32(h + 128, 1000);       // dwScale
    avi_p32(h + 132, fps_milli);  // dwRate: rate/scale = fps
    avi_p32(h + 136, 0);          // dwStart
    avi_p32(h + 140, frames);     // dwLength
    avi_p32(h + 144, max_chunk);  // dwSuggestedBufferSize
    avi_p32(h + 148, 0xFFFFFFFFu);  // dwQuality
    avi_p32(h + 152, 0);          // dwSampleSize (0 = moi mau 1 chunk)
    avi_p16(h + 156, 0);          // rcFrame left
    avi_p16(h + 158, 0);          // top
    avi_p16(h + 160, w);          // right
    avi_p16(h + 162, ht);         // bottom
    avi_tag(h + 164, "strf");
    avi_p32(h + 168, 40);
    avi_p32(h + 172, 40);         // biSize
    avi_p32(h + 176, w);
    avi_p32(h + 180, ht);
    avi_p16(h + 184, 1);          // biPlanes
    avi_p16(h + 186, 24);         // biBitCount
    avi_tag(h + 188, "MJPG");     // biCompression
    avi_p32(h + 192, w * ht * 3); // biSizeImage
    // biXPels, biYPels, biClrUsed, biClrImportant = 0 (h + 196..211)
    // LIST movi
    avi_tag(h + 212, "LIST");
    avi_p32(h + 216, 4 + chunk_bytes);
    avi_tag(h + 220, "movi");
}

// Mot muc idx1 (16 byte). offset tinh tu chu 'movi'.
static inline void avi_idx_entry(uint8_t *e, uint32_t offset, uint32_t len)
{
    avi_tag(e, "00dc");
    avi_p32(e + 4, 0x10);  // AVIIF_KEYFRAME (moi khung JPEG la khung khoa)
    avi_p32(e + 8, offset);
    avi_p32(e + 12, len);
}

// Kich thuoc chunk '00dc' tren file: 8 + len + 1 byte dem neu le.
static inline uint32_t avi_chunk_size(uint32_t len)
{
    return AVI_CHUNK_HDR + len + (len & 1u);
}

// Doc kich thuoc anh tu marker SOFn cua JPEG. false neu khong thay.
static inline bool avi_jpeg_dims(const uint8_t *b, size_t n, uint32_t *w, uint32_t *ht)
{
    if (n < 4 || b[0] != 0xFF || b[1] != 0xD8) {
        return false;
    }
    size_t i = 2;
    while (i + 4 <= n) {
        if (b[i] != 0xFF) {
            i++;
            continue;
        }
        uint8_t m = b[i + 1];
        if (m == 0xFF) {
            i++;
            continue;
        }
        if (m == 0xD8 || m == 0x01 || (m >= 0xD0 && m <= 0xD7)) {
            i += 2;
            continue;
        }
        if (m == 0xD9 || m == 0xDA) {
            return false;
        }
        size_t seg = ((size_t)b[i + 2] << 8) | b[i + 3];
        if (m >= 0xC0 && m <= 0xCF && m != 0xC4 && m != 0xC8 && m != 0xCC) {
            if (i + 9 > n) {
                return false;
            }
            *ht = ((uint32_t)b[i + 5] << 8) | b[i + 6];
            *w = ((uint32_t)b[i + 7] << 8) | b[i + 8];
            return *w > 0 && *ht > 0;
        }
        if (seg < 2) {
            return false;
        }
        i += 2 + seg;
    }
    return false;
}
