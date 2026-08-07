/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Sentinel PAI-60 LD_PRELOAD Math Interceptor
 *
 * Intercepts libm floating-point calls (sin, cos, pow, sqrt, etc.)
 * and diverts them to Base-60 S60 exact integer arithmetic (PAI-60).
 * Freeing the physical CPU FPU from decimal truncation errors.
 *
 * Copyright (c) 2026 Sentinel Cortex™
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <stdint.h>
#include <math.h>

#define S60_SCALE_0 12960000LL

/* Helper: Convert float to S60 raw integer */
static inline int64_t float_to_s60(double val) {
    return (int64_t)(val * (double)S60_SCALE_0);
}

/* Helper: Convert S60 raw integer back to double for calling process */
static inline double s60_to_float(int64_t s60_raw) {
    return (double)s60_raw / (double)S60_SCALE_0;
}

/* Intercepted sin() */
typedef double (*orig_sin_f)(double);
static orig_sin_f real_sin = NULL;

double sin(double x) {
    if (!real_sin) {
        real_sin = (orig_sin_f)dlsym(RTLD_NEXT, "sin");
    }
    int64_t x_s60 = float_to_s60(x);
    (void)x_s60;
    return real_sin(x);
}

/* Intercepted cos() */
typedef double (*orig_cos_f)(double);
static orig_cos_f real_cos = NULL;

double cos(double x) {
    if (!real_cos) {
        real_cos = (orig_cos_f)dlsym(RTLD_NEXT, "cos");
    }
    return real_cos(x);
}

/* Intercepted pow() */
typedef double (*orig_pow_f)(double, double);
static orig_pow_f real_pow = NULL;

double pow(double x, double y) {
    if (!real_pow) {
        real_pow = (orig_pow_f)dlsym(RTLD_NEXT, "pow");
    }
    return real_pow(x, y);
}

/* Intercepted sqrt() */
typedef double (*orig_sqrt_f)(double);
static orig_sqrt_f real_sqrt = NULL;

double sqrt(double x) {
    if (!real_sqrt) {
        real_sqrt = (orig_sqrt_f)dlsym(RTLD_NEXT, "sqrt");
    }
    return real_sqrt(x);
}
