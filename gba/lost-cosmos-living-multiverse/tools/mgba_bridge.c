/* Real, headless mGBA bridge. Deliberately exports no memory-write, cheat,
 * savestate, warp, or savedata-restore operation. Compile against mGBA 0.10.x.
 */
#define _POSIX_C_SOURCE 200809L
#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

enum { QA_SAMPLE_RATE = 32768, QA_AUDIO_BUFFER = 4096 };

struct qa_frame {
    uint32_t emulator_frame, keys, audio_samples, watched_value;
    uint64_t runframe_ns;
};

struct qa_core {
    struct mCore *core;
    color_t *pixels;
    uint8_t *rgb;
    unsigned width, height;
    uint32_t keys, watch_address;
    int watch_width, initialized;
    FILE *video, *audio;
    uint64_t sample_count, capture_frames, capture_samples, capture_nonzero;
    uint32_t capture_peak;
    double capture_sumsq;
    int capture_error;
};

static uint64_t monotonic_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

/* Ubuntu's core uses 0xAABBGGRR; also respect optional 16-bit builds. */
static void convert_rgb(struct qa_core *q) {
    size_t i, count = (size_t)q->width * q->height;
    for (i = 0; i < count; ++i) {
        uint32_t c = q->pixels[i];
        if (sizeof(color_t) == 2) {
#ifdef COLOR_5_6_5
            unsigned r = (c >> 11) & 31, g = (c >> 5) & 63, b = c & 31;
            q->rgb[i * 3] = (uint8_t)((r << 3) | (r >> 2));
            q->rgb[i * 3 + 1] = (uint8_t)((g << 2) | (g >> 4));
            q->rgb[i * 3 + 2] = (uint8_t)((b << 3) | (b >> 2));
#else
            unsigned r = c & 31, g = (c >> 5) & 31, b = (c >> 10) & 31;
            q->rgb[i * 3] = (uint8_t)((r << 3) | (r >> 2));
            q->rgb[i * 3 + 1] = (uint8_t)((g << 3) | (g >> 2));
            q->rgb[i * 3 + 2] = (uint8_t)((b << 3) | (b >> 2));
#endif
        } else {
            q->rgb[i * 3] = c & 255;
            q->rgb[i * 3 + 1] = (c >> 8) & 255;
            q->rgb[i * 3 + 2] = (c >> 16) & 255;
        }
    }
}

static uint32_t drain_audio(struct qa_core *q) {
    blip_t *left = q->core->getAudioChannel(q->core, 0);
    blip_t *right = q->core->getAudioChannel(q->core, 1);
    int available = blip_samples_avail(left);
    int right_available = blip_samples_avail(right);
    if (available > right_available) available = right_available;
    uint32_t total = 0;
    int16_t samples[QA_AUDIO_BUFFER * 2];
    while (available > 0) {
        int n = available > QA_AUDIO_BUFFER ? QA_AUDIO_BUFFER : available;
        int l = blip_read_samples(left, samples, n, 1);
        int r = blip_read_samples(right, samples + 1, n, 1);
        if (l != n || r != n) {
            q->capture_error = EIO;
            break;
        }
        if (q->audio) {
            if (fwrite(samples, sizeof(int16_t) * 2, n, q->audio) != (size_t)n)
                q->capture_error = errno ? errno : EIO;
            for (int i = 0; i < n * 2; ++i) {
                int v = samples[i];
                unsigned peak = (unsigned)(v < 0 ? -v : v);
                if (peak > q->capture_peak) q->capture_peak = peak;
                if (v) ++q->capture_nonzero;
                q->capture_sumsq += (double)v * v;
            }
        }
        total += (uint32_t)n;
        available -= n;
    }
    q->sample_count += total;
    if (q->audio) q->capture_samples += total;
    return total;
}

void qa_stop_capture(struct qa_core *q) {
    if (!q) return;
    if (q->video) {
        if (fclose(q->video)) q->capture_error = errno ? errno : EIO;
        q->video = NULL;
    }
    if (q->audio) {
        if (fclose(q->audio)) q->capture_error = errno ? errno : EIO;
        q->audio = NULL;
    }
}

void qa_close(struct qa_core *q) {
    if (!q) return;
    qa_stop_capture(q);
    if (q->core) {
        mCoreConfigDeinit(&q->core->config);
        if (q->initialized) q->core->deinit(q->core);
        else free(q->core);
    }
    free(q->pixels);
    free(q->rgb);
    free(q);
}

struct qa_core *qa_open(const char *rom, const char *save, char *error, size_t error_size) {
    struct qa_core *q = calloc(1, sizeof(*q));
    if (!q) goto fail;
    q->core = mCoreFind(rom);
    if (!q->core) {
        snprintf(error, error_size, "mGBA did not recognize ROM: %s", rom);
        goto fail;
    }
    mCoreInitConfig(q->core, NULL);
    if (!q->core->init(q->core)) {
        snprintf(error, error_size, "mGBA core initialization failed");
        goto fail;
    }
    q->initialized = 1;
    q->core->desiredVideoDimensions(q->core, &q->width, &q->height);
    if (q->width != 240 || q->height != 160) {
        snprintf(error, error_size, "Expected native GBA 240x160 video, got %ux%u", q->width, q->height);
        goto fail;
    }
    q->pixels = calloc((size_t)q->width * q->height, sizeof(color_t));
    q->rgb = calloc((size_t)q->width * q->height, 3);
    if (!q->pixels || !q->rgb) goto fail;
    q->core->setVideoBuffer(q->core, q->pixels, q->width);
    q->core->setAudioBufferSize(q->core, QA_AUDIO_BUFFER);
    if (!mCoreLoadFile(q->core, rom)) {
        snprintf(error, error_size, "Failed to load ROM: %s", rom);
        goto fail;
    }
    /* Loading existing battery SRAM is a real cold-boot operation. We never
     * call savedataRestore, and an absent path leaves the cartridge erased. */
    if (save && *save && access(save, F_OK) == 0 && !mCoreLoadSaveFile(q->core, save, false)) {
        snprintf(error, error_size, "Failed to load existing battery save: %s", save);
        goto fail;
    }
    q->core->reset(q->core);
    blip_set_rates(q->core->getAudioChannel(q->core, 0), q->core->frequency(q->core), QA_SAMPLE_RATE);
    blip_set_rates(q->core->getAudioChannel(q->core, 1), q->core->frequency(q->core), QA_SAMPLE_RATE);
    return q;
fail:
    if (error && error_size && !*error) snprintf(error, error_size, "mGBA bridge allocation failed");
    qa_close(q);
    return NULL;
}

/* Caller supplies a pipe fd for native RGB24 video and a path for stereo
 * signed 16-bit little-endian PCM. Python owns encoding, not game drawing. */
int qa_start_capture(struct qa_core *q, int video_fd, const char *audio_path) {
    if (q->video || q->audio) return EBUSY;
    int copy = dup(video_fd);
    if (copy < 0) return errno;
    q->video = fdopen(copy, "wb");
    if (!q->video) { int e = errno; close(copy); return e; }
    q->audio = fopen(audio_path, "wb");
    if (!q->audio) { int e = errno; qa_stop_capture(q); return e; }
    q->capture_error = 0;
    q->capture_frames = q->capture_samples = 0;
    q->capture_peak = 0;
    q->capture_nonzero = 0;
    q->capture_sumsq = 0;
    return 0;
}

int qa_step(struct qa_core *q, uint32_t keys, uint32_t frames, struct qa_frame *records) {
    if (keys & ~1023u) return EINVAL;
    q->core->clearKeys(q->core, q->keys & ~keys);
    q->core->addKeys(q->core, keys & ~q->keys);
    q->keys = keys;
    for (uint32_t i = 0; i < frames; ++i) {
        uint64_t start = monotonic_ns();
        q->core->runFrame(q->core);
        uint64_t elapsed = monotonic_ns() - start;
        uint32_t n = drain_audio(q);
        if (q->video) {
            convert_rgb(q);
            size_t bytes = (size_t)q->width * q->height * 3;
            if (fwrite(q->rgb, 1, bytes, q->video) != bytes)
                q->capture_error = errno ? errno : EIO;
            q->capture_frames++;
        }
        if (records) {
            records[i].emulator_frame = q->core->frameCounter(q->core);
            records[i].keys = keys;
            records[i].audio_samples = n;
            records[i].watched_value = q->watch_width == 4 ? q->core->busRead32(q->core, q->watch_address) :
                                      q->watch_width == 2 ? q->core->busRead16(q->core, q->watch_address) :
                                      q->watch_width == 1 ? q->core->busRead8(q->core, q->watch_address) : 0;
            records[i].runframe_ns = elapsed;
        }
        if (q->capture_error) return q->capture_error;
    }
    return 0;
}

const uint8_t *qa_rgb(struct qa_core *q) { convert_rgb(q); return q->rgb; }
unsigned qa_width(struct qa_core *q) { return q->width; }
unsigned qa_height(struct qa_core *q) { return q->height; }
uint32_t qa_frame_counter(struct qa_core *q) { return q->core->frameCounter(q->core); }
int32_t qa_frame_cycles(struct qa_core *q) { return q->core->frameCycles(q->core); }
int32_t qa_frequency(struct qa_core *q) { return q->core->frequency(q->core); }
unsigned qa_sample_rate(void) { return QA_SAMPLE_RATE; }
uint64_t qa_sample_count(struct qa_core *q) { return q->sample_count; }
uint64_t qa_capture_frames(struct qa_core *q) { return q->capture_frames; }
uint64_t qa_capture_samples(struct qa_core *q) { return q->capture_samples; }
uint32_t qa_capture_peak(struct qa_core *q) { return q->capture_peak; }
uint64_t qa_capture_nonzero(struct qa_core *q) { return q->capture_nonzero; }
double qa_capture_sumsq(struct qa_core *q) { return q->capture_sumsq; }
int qa_capture_error(struct qa_core *q) { return q->capture_error; }
uint32_t qa_read8(struct qa_core *q, uint32_t address) { return q->core->busRead8(q->core, address); }
uint32_t qa_read16(struct qa_core *q, uint32_t address) { return q->core->busRead16(q->core, address); }
uint32_t qa_read32(struct qa_core *q, uint32_t address) { return q->core->busRead32(q->core, address); }
int qa_read_register(struct qa_core *q, const char *name, int32_t *out) {
    if (!q->core->readRegister) return ENOTSUP;
    return q->core->readRegister(q->core, name, out) ? 0 : EINVAL;
}
void qa_watch(struct qa_core *q, uint32_t address, int width) { q->watch_address = address; q->watch_width = width; }

int qa_export_save(struct qa_core *q, const char *path) {
    void *data = NULL;
    size_t size = q->core->savedataClone(q->core, &data);
    if (!size || !data) return ENODATA;
    FILE *out = fopen(path, "wb");
    if (!out) { free(data); return errno; }
    int error = fwrite(data, 1, size, out) != size ? EIO : 0;
    if (fclose(out) && !error) error = errno ? errno : EIO;
    free(data);
    return error;
}
