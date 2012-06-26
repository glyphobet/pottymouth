# Run with:
# % python generate_javascript_tests.py > ../javascript/generated_tests.js
import inspect
from pottymouth import Node
from tests import basic_tests

class JavaScriptTestGenerator(basic_tests):
    def _helper(self, source, expected):
        if isinstance(source, str):
            source = source.decode('utf8')
        print(u"""    equal(p.parse(%s).toString(),\n      %r,\n      '%s');""" % (
            repr(source)[1:], # strip off the u prefix
            str(Node('div', *expected)).decode('utf8').encode('ascii', errors='xmlcharrefreplace'),
            inspect.stack()[1][3]
        ))

if __name__ == '__main__':
    jstestgen = JavaScriptTestGenerator()
    for f in sorted(dir(jstestgen)):
        if callable(getattr(jstestgen, f)) and f.startswith('test_'):
            try:
                getattr(jstestgen, f)()
            except Exception as exc:
                print "    // Skipped %s" % f
