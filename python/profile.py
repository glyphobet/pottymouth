#!/usr/bin/env python
from test import basic_tests

class profiler(basic_tests):
    def __init__(self):
        self.setup()
        for f in dir(self):
            if f.startswith('test_'):
                getattr(self, f)()

    def _helper(self, source, output):
        self.parser.parse(source)

if __name__ == '__main__':
    import cProfile, pstats
    cProfile.run('profiler()', '/tmp/pottymouth_profile')
    stats = pstats.Stats('/tmp/pottymouth_profile')
    stats.strip_dirs().sort_stats('time', 'cum').print_stats(25)
