#!/usr/bin/env python3
s='unsigned long pat_len = __VERIFIER_nondet_ulong(), unsigned long a_len = __VERIFIER_nondet_ulong();'
s='unsigned long a_len = __VERIFIER_nondet_ulong();'
res= s.split(',')
print(res)
for ss in res:
    _, right = ss.split("=")
    left, _ = right.split(";")
    assert(len(right) > 0)
    if left[-1] == "f" or left[-1] == "l":
        left = left[:-1]
    print(left,right)