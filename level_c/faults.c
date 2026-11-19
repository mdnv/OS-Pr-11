#define _POSIX_C_SOURCE 200809L
/* Уровень C: реальные page faults и локальность обхода массива.
   Компиляция: gcc -std=c11 -Wall -Wextra -O2 -o faults level_c/faults.c */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

#define MIB (1024UL * 1024UL)
#define SIDE 2048UL
#define REPEATS 3

static int usage(struct rusage *out) {
    if (getrusage(RUSAGE_SELF, out) != 0) {
        perror("getrusage");
        return -1;
    }
    return 0;
}

static void print_delta(const char *label, const struct rusage *before,
                        const struct rusage *after) {
    printf("%-16s minor=%ld major=%ld\n", label,
           (long)(after->ru_minflt - before->ru_minflt),
           (long)(after->ru_majflt - before->ru_majflt));
}

#ifdef __linux__
/* В /proc/self/stat: поле 10 = minflt, поле 12 = majflt.
   После последней ')' начинаются поля, первое — номер 3 (state).
   Парсинг с учётом пробелов в comm, а не наивный scanf всех полей. */
static int proc_stat_faults(unsigned long long *minor,
                            unsigned long long *major) {
    FILE *fp = fopen("/proc/self/stat", "r");
    if (!fp) return -1;
    char line[8192];
    if (!fgets(line, sizeof(line), fp)) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    char *right = strrchr(line, ')');
    if (!right) return -1;
    int field = 3;
    int found_minor = 0, found_major = 0;
    char *save = NULL;
    for (char *tok = strtok_r(right + 1, " \t\n", &save);
         tok != NULL; tok = strtok_r(NULL, " \t\n", &save), ++field) {
        if (field == 10) {
            *minor = strtoull(tok, NULL, 10);
            found_minor = 1;
        }
        if (field == 12) {
            *major = strtoull(tok, NULL, 10);
            found_major = 1;
            break;
        }
    }
    return found_minor && found_major ? 0 : -1;
}
#endif

static double seconds(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t) != 0) {
        perror("clock_gettime");
        exit(EXIT_FAILURE);
    }
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

static int array_benchmark(void) {
    const size_t cells = SIDE * SIDE;
    uint32_t *data = malloc(cells * sizeof(*data));
    if (!data) {
        perror("malloc matrix");
        return 1;
    }
    /* До отсчёта времени выделим физические страницы. */
    memset(data, 0, cells * sizeof(*data));
    volatile uint32_t *a = data; /* не даём компилятору удалить запись */

    double start = seconds();
    for (int repeat = 0; repeat < REPEATS; ++repeat) {
        for (size_t row = 0; row < SIDE; ++row) {
            for (size_t col = 0; col < SIDE; ++col) {
                a[row * SIDE + col] += 1;
            }
        }
    }
    double row_time = seconds() - start;

    start = seconds();
    for (int repeat = 0; repeat < REPEATS; ++repeat) {
        for (size_t col = 0; col < SIDE; ++col) {
            for (size_t row = 0; row < SIDE; ++row) {
                a[row * SIDE + col] += 1;
            }
        }
    }
    double col_time = seconds() - start;

    printf("\n2D array %lux%lu, %d passes each (~%lu MiB):\n",
           (unsigned long)SIDE, (unsigned long)SIDE, REPEATS,
           (unsigned long)(cells * sizeof(*data) / MIB));
    printf("by rows:    %.6f s\n", row_time);
    printf("by columns: %.6f s\n", col_time);
    if (row_time > 0.0) printf("columns/rows: %.2fx\n", col_time / row_time);
    printf("checksum sample: %" PRIu32 "\n", data[0]);

    free(data);
    return 0;
}

int main(void) {
    const size_t size = 64UL * MIB;
    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size < 1) {
        fprintf(stderr, "Cannot find system page size\n");
        return 1;
    }

    struct rusage before, after;
    if (usage(&before) != 0) return 1;
    unsigned char *mem = malloc(size);
    if (!mem) {
        perror("malloc 64 MiB");
        return 1;
    }
    if (usage(&after) != 0) {
        free(mem);
        return 1;
    }
    printf("Page size: %ld B; 64 MiB / page size = %lu pages\n", page_size,
           (unsigned long)(size / (size_t)page_size));
    print_delta("malloc 64 MiB:", &before, &after);
    before = after;

    volatile unsigned char *touch = mem;
    for (size_t offset = 0; offset < size; offset += (size_t)page_size) {
        touch[offset] = (unsigned char)(offset / (size_t)page_size);
    }
    if (usage(&after) != 0) {
        free(mem);
        return 1;
    }
    print_delta("first touch:", &before, &after);
    printf("NOTE: Results depend on OS; major faults can stay 0.\n");

#ifdef __linux__
    unsigned long long minor = 0, major = 0;
    if (proc_stat_faults(&minor, &major) == 0) {
        printf("/proc/self/stat (total): minflt=%llu majflt=%llu\n", minor, major);
    }
#endif
    free(mem);
    return array_benchmark();
}
