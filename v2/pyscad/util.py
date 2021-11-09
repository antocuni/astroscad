import sys
import os
import textwrap
import traceback
from PIL import Image
from .camera import Camera

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


def render_to_PIL(obj, **kwargs):
    png = '/tmp/autorender.png'
    obj.render_to_image(png, **kwargs)
    img = Image.open(png)
    img.load()
    return img

def render_to_collage(obj, filename, distance=None):
    cameras = [Camera.DEFAULT, Camera.TOP, Camera.FRONT, Camera.RIGHT]
    if distance is not None:
        cameras = [cam.with_distance(distance) for cam in cameras]

    filename = os.fspath(filename)
    size = 512, 512  # size of each frame
    a = render_to_PIL(obj, size=size, camera=cameras[0])
    b = render_to_PIL(obj, size=size, camera=cameras[1])
    c = render_to_PIL(obj, size=size, camera=cameras[2])
    d = render_to_PIL(obj, size=size, camera=cameras[3])
    #
    w, h = size
    final_size = (w*2 + 2, h*2 + 2)
    res = Image.new("RGBA", final_size, color='black')
    res.paste(a, (0,   0))     # upper left
    res.paste(b, (w+2, 0))     # upper right
    res.paste(c, (0,   h+2))   # lower left
    res.paste(d, (w+2, h+2))   # lower right
    res.save(filename)
