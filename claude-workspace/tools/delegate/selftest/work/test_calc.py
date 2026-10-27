# Gate cua bai thu delegate.py – Claude viet, executor KHONG sua file nay.
from calc import add, clamp

assert add(2, 3) == 5
assert clamp(5, 0, 3) == 3 and clamp(-1, 0, 3) == 0 and clamp(2, 0, 3) == 2
print("gate OK")
