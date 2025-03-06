from .pure import test as test_pure
from .avx2 import test as test_avx2
from .avx512 import test as test_avx512

import platform


def test(rvs, use_avx=3, **kwargs):
    if platform.processor() != 'arm':
        from cpufeature.extension import CPUFeature
    try:
        if not CPUFeature:
            CPUFeature = {
                'AVX512vl': False,
                'AVX2': False
            }
    except NameError:
        CPUFeature = {
            'AVX512vl': False,
            'AVX2': False
        }
    method = test_pure
    if use_avx == 1 and not CPUFeature['AVX512vl']:
        print("!!! Warning: AVX512vl instruction set is not supported by your CPU, backing up to pure implementation")
        use_avx = 0
    elif use_avx in (1, 3) and CPUFeature['AVX512vl']:
        method = test_avx512
        use_avx = 1
    elif use_avx == 2 and not CPUFeature['AVX2']:
        print("!!! Warning: AVX2 instruction set is not supported by your CPU, backing up to pure implementation")
        use_avx = 0
    elif use_avx in (2, 3) and CPUFeature['AVX2']:
        method = test_avx2
        use_avx = 2
    else:  # use pure implementation
        use_avx = 0

    return method(rvs, use_avx=use_avx, **kwargs)
