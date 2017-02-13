# -*- encoding: utf-8 -*-

def min_length(arr, length, fill=None):
    return arr + [fill] * (length - len(arr))
