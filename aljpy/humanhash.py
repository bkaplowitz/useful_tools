import uuid
import hashlib
from pkg_resources import resource_string
from . import cache

__all__ = ('humanhash')

@cache.memcache()
def nouns():
    nouns = resource_string(__package__, 'humanhashnouns.txt').decode().split('\r\n')
    # Six-char-or-less nouns make up half the list
    return [n for n in nouns if len(n) <= 6]

@cache.memcache()
def adjectives():
    adjs = resource_string(__package__, 'humanhashadjectives.txt').decode().split('\n')
    # Six-char-or-less adjectives make up half the list
    return [a for a in adjs if len(a) <= 6]

def humanhash(s=None, n=3):
    """Hashes `s` into a sentence of hash-separated words. The first `n-1` are adjectives; the last is a noun.
    
    There are 600 adjectives and 2500 nouns, so the default hash space has 4bn members.
    """
    if s is None:
        return humanhash(str(uuid.uuid4()), n=n)

    bs = s.encode()
    ints = []
    for _ in range(n):
        m = hashlib.md5()
        m.update(bs)
        bs = m.digest()
        ints.append(int.from_bytes(bs[-32:], 'big', signed=False))
    adjs, ns = adjectives(), nouns()
    words = [adjs[i % len(adjs)] for i in ints[:-1]] + [ns[ints[-1] % len(ns)]]
    return '-'.join(words)