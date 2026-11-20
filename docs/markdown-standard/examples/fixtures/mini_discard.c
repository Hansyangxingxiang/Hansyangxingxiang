/* Synthetic fixture for documentation examples. Not production code. */
#include <stdint.h>

#define MIN_DISCARD_BYTES 4096u

struct discard_req {
    uint64_t offset;
    uint64_t length;
};

static int align_ok(uint64_t value, uint32_t gran)
{
    return gran != 0 && (value % gran) == 0;
}

int example_discard_check(const struct discard_req *req, uint32_t gran)
{
    if (req == 0 || gran == 0) {
        return -1;
    }
    if (req->length < MIN_DISCARD_BYTES) {
        return -2;
    }
    if (!align_ok(req->offset, gran) || !align_ok(req->length, gran)) {
        return -3;
    }
    return 0;
}
