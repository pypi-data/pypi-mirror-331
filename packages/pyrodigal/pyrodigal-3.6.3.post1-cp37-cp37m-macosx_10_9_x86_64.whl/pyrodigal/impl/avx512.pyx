# coding: utf-8
# cython: language_level=3, linetrace=True, binding=True

from libc.stdint cimport int8_t, uint8_t

from ..lib cimport BaseConnectionScorer

cdef extern from "avx512.h" nogil:
    void skippable_avx512(const int8_t*, const uint8_t*, const uint8_t*, const int, const int, uint8_t*) noexcept

cdef class AVX512ConnectionScorer(BaseConnectionScorer):
    def __cinit__(self):
        self.skippable = skippable_avx512
        self.enabled = True
