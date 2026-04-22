import math


def estimate_bruteforce_time(length, charset_size, guesses_per_sec=1_000_000):
    combinations = charset_size ** length
    seconds = combinations / guesses_per_sec
    return seconds


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} sec"
    elif seconds < 3600:
        return f"{seconds/60:.2f} min"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} h"
    else:
        return f"{seconds/86400:.2f} days"