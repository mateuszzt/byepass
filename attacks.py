import itertools
import time


def brute_force(target_hash, charset, max_length, hash_func, salt, progress_callback=None):
    start = time.time()
    total = sum(len(charset) ** i for i in range(1, max_length + 1))
    checked = 0

    for length in range(1, max_length + 1):
        for attempt in itertools.product(charset, repeat=length):
            attempt = ''.join(attempt)
            checked += 1

            if progress_callback:
                progress_callback(checked / total)

            if hash_func(attempt, salt) == target_hash:
                return attempt, time.time() - start

    return None, time.time() - start


def dictionary_attack(target_hash, wordlist_path, hash_func, salt):
    start = time.time()

    with open(wordlist_path, "r", encoding="utf-8") as f:
        for word in f:
            word = word.strip()
            if hash_func(word, salt) == target_hash:
                return word, time.time() - start

    return None, time.time() - start