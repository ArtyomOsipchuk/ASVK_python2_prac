"""This is module."""
import sys
from math import sin


def thefun(a, b, c):
    """Funning func."""
    return int(a) / int(b) + sin(int(c))


c = sys.argv[1]
a = b = c
print(thefun(a, b, c))
