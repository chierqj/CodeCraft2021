#include "log.h"

#ifdef USE_LOG

#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <mutex>

using namespace std;
std::mutex global_log_mutex;

static struct {
    void *udata;
    log_LockFn lock;
    FILE *fp;
    int level;
    int quiet;
} L;

static const char *level_names[] = {"TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"};
#ifndef LOG_USE_COLOR
#define LOG_USE_COLOR
#endif
#ifdef LOG_USE_COLOR
static const char *level_colors[] = {"\x1b[94m", "\x1b[36m", "\x1b[32m", "\x1b[33m", "\x1b[31m", "\x1b[35m"};
#endif

static void lock(void) {
#ifndef LOCAL_DEBUG
    return;
#endif
    if (L.lock) {
        L.lock(L.udata, 1);
    }
}

static void unlock(void) {
#ifndef LOCAL_DEBUG
    return;
#endif
    if (L.lock) {
        L.lock(L.udata, 0);
    }
}

void log_set_udata(void *udata) {
#ifndef LOCAL_DEBUG
    return;
#endif
    L.udata = udata;
}

void log_set_lock(log_LockFn fn) {
#ifndef LOCAL_DEBUG
    return;
#endif
    L.lock = fn;
}

void log_set_fp(FILE *fp) {
#ifndef LOCAL_DEBUG
    return;
#endif
    L.fp = fp;
}

void log_set_level(int level) {
#ifndef LOCAL_DEBUG
    return;
#endif
    L.level = level;
}

void log_set_quiet(int enable) {
#ifndef LOCAL_DEBUG
    return;
#endif
    L.quiet = enable ? 1 : 0;
}

void log_log(int level, const char *file, int line, const char *fmt, ...) {
#ifndef LOCAL_DEBUG
    return;
#endif

    if (level < L.level) {
        return;
    }

    using namespace std::chrono;
    {
        unique_lock<mutex> lock_global(global_log_mutex);
        /* Acquire lock */
        lock();

        /* Get current time */
        time_t t = time(nullptr);
        struct tm *lt = localtime(&t);

        /* Log to stderr */
        if (!L.quiet) {
            va_list args;
            char buf[32];
#ifdef LOG_USE_COLOR
            // fprintf(stderr, "%s %s%-5s\x1b[0m \x1b[90m%s:%d:\x1b[0m ", buf, level_colors[level], level_names[level],
            //         file, line);
            fprintf(stderr, "%s %s%-5s\x1b[0m \x1b[90m%s:%d:\x1b[0m ", buf, level_colors[level], level_names[level],
                    file, line);
#else
            fprintf(stderr, "%s %-5s %s:%d: ", buf, level_names[level], file, line);
#endif
            va_start(args, fmt);
            vfprintf(stderr, fmt, args);
            va_end(args);
            fprintf(stderr, "\n");
        }

        /* Log to file */
        if (L.fp) {
            va_list args;
            char buf[32];
            buf[strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", lt)] = '\0';
            fprintf(L.fp, "%s %-5s: ", buf, level_names[level]);
            va_start(args, fmt);
            vfprintf(L.fp, fmt, args);
            va_end(args);
            fprintf(L.fp, "\n");
            fflush(L.fp);
        }

        /* Release lock */
        unlock();
    }
}

void log_log_without_file_name(int level, const char *fmt, ...) {
#ifndef LOCAL_DEBUG
    return;
#endif
    if (level < L.level) {
        return;
    }

    using namespace std::chrono;
    time_point<high_resolution_clock> clock_now = high_resolution_clock::now();
    {
        unique_lock<mutex> lock_global(global_log_mutex);
        /* Acquire lock */
        lock();

        /* Get current time */
        time_t t = time(nullptr);
        struct tm *lt = localtime(&t);

        /* Log to stderr */
        if (!L.quiet) {
            va_list args;
            char buf[16];
            buf[strftime(buf, sizeof(buf), "%H:%M:%S", lt)] = '\0';
#ifdef LOG_USE_COLOR
            fprintf(stderr, "%s %s%-5s\x1b[0m \x1b[90m(ts: %.6lf):\x1b[0m ", buf, level_colors[level],
                    level_names[level],
                    duration_cast<nanoseconds>(clock_now.time_since_epoch()).count() / 1000000000.0);
#else
            fprintf(stderr, "%s %-5s (ts: %.6lf) %s:%d: ", buf, level_names[level],
                    duration_cast<nanoseconds>(clock_now.time_since_epoch()).count() / 1000000000.0, file, line);
#endif
            va_start(args, fmt);
            vfprintf(stderr, fmt, args);
            va_end(args);
            fprintf(stderr, "\n");
        }

        /* Log to file */
        if (L.fp) {
            va_list args;
            char buf[32];
            buf[strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", lt)] = '\0';
            fprintf(L.fp, "%s %-5s (ts: %.6lf): ", buf, level_names[level],
                    duration_cast<nanoseconds>(clock_now.time_since_epoch()).count() / 1000000000.0);
            va_start(args, fmt);
            vfprintf(L.fp, fmt, args);
            va_end(args);
            fprintf(L.fp, "\n");
            fflush(L.fp);
        }

        /* Release lock */
        unlock();
    }
}

#endif
