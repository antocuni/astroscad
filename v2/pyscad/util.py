import sys
import textwrap
import traceback

def in2mm(inches):
    return inches * 25.4

class InvalidAnchorError(Exception):
    pass

class InvalidAnchorPoints:

    def __init__(self, old_anchors):
        # format the traceback but ignore the __init__ and the call to
        # format_stack itself
        frame = sys._getframe(2)
        tb = traceback.format_stack(frame)
        self._old_anchors = old_anchors
        self._traceback = ''.join(tb)

    def has_point(self, name):
        return self._old_anchors.has_point(name)

    def __getattr__(self, name):
        if not self.has_point(name):
            raise AttributeError(name)
        msg = 'AnchorPoints have been invalidated here:\n'
        msg += textwrap.indent(self._traceback, '    ')
        raise InvalidAnchorError(msg)

    def translate(self, v):
        pass
