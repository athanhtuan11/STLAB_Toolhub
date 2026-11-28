#include "owl_pic.h"

lv_obj_t* OwlPicCreate(lv_obj_t* parent, const lv_image_dsc_t* dsc, int cx, int cy, int px) {
    const int w = static_cast<int>(dsc->header.w);
    const int h = static_cast<int>(dsc->header.h);
    lv_obj_t* img = lv_image_create(parent);
    lv_image_set_src(img, dsc);
    lv_image_set_pivot(img, w / 2, h / 2);
    lv_image_set_scale(img, static_cast<uint32_t>(256 * px / w));
    lv_image_set_antialias(img, true);
    lv_obj_set_pos(img, cx - w / 2, cy - h / 2);
    return img;
}
