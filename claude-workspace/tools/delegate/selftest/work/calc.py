def add(a, b):
    """Return the sum of a and b."""
    return a + b


def clamp(x, lo, hi):
    """Limit x to the inclusive range [lo, hi]."""
    return max(lo, min(x, hi))
