import io
import contextlib
import sys

class StdoutRedirector(io.StringIO):
    def __init__(self, target):
        io.StringIO.__init__(self)
        self.target = target
    
    def write(self, string):
        self.target.append(string)
        io.StringIO.write(self, string)

output_lines = []
stdout_redirector = StdoutRedirector(output_lines)

@contextlib.contextmanager
def stdout_redirect(redirector):
    original = sys.stdout
    sys.stdout = redirector
    try:
        yield
    finally:
        sys.stdout = original