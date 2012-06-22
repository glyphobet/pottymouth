import inspect

from pottymouth import Node

from test import basic_tests

class JavaScriptTestGenerator(basic_tests):
    def _helper(self, source, expected):
        # import pdb; pdb.set_trace()
        print u"""    equal(p.parse(%r).toString(),\n      %r,\n      '%s');""" % (
            source,
            str(Node('div', *expected)),
            inspect.stack()[1][3]
        )

if __name__ == '__main__':
    jstestgen = JavaScriptTestGenerator()
    for f in sorted(dir(jstestgen)):
        if callable(getattr(jstestgen, f)) and f.startswith('test_'):
            try:
                getattr(jstestgen, f)()
            except Exception as exc:
                # raise
                print "    // Skipped %s" % f
