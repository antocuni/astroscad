import functools
import solid
from .geometry import Point, Vector, AnchorPoints
from .util import InvalidAnchorPoints
from .autorender import autorender

EPSILON = 0.001

def in2mm(inches):
    return inches * 25.4


class PySCADObject:
    """
    This is a wrapper around solid.OpenSCADObject, so that we can add our own
    functionalities
    """

    def __init__(self, *args, **kwargs):
        self.anchors = AnchorPoints()
        self.obj = None
        self.make_obj(*args, **kwargs)
        assert self.obj is not None

    def make_obj(self, *args, **kwargs):
        raise NotImplementedError

    def autorender(self, *, filename='/tmp/autorender.scad', **kwargs):
        autorender(self, filename, **kwargs)

    def render_to_file(self, filename, *, fa=1, fs=0.4, fn=None):
        header = []
        if fn: header.append(f'$fn = {fn};')
        if fa: header.append(f'$fa = {fa};')
        if fs: header.append(f'$fs = {fs};')
        header = '\n'.join(header)
        return solid.scad_render_to_file(self.obj, filename, file_header=header)

    def __getattr__(self, name):
        if self.anchors.has_point(name):
            return getattr(self.anchors, name)
        raise AttributeError(name)

    def invalidate_anchors(self):
        self.anchors = InvalidAnchorPoints(self.anchors)

    def move_to(self, **kwargs):
        for anchor, new_p in kwargs.items():
            current_p = getattr(self.anchors, anchor)
            v = new_p - current_p
            self.translate(v.x, v.y, v.z)
        return self

    def show_bounding_box(self):
        if not self.anchors.has_point('pmin') or not self.anchors.has_point('pmax'):
            raise ValueError('Cannot find a bounding box')
        size = self.pmax - self.pmin
        bbox = Cube(size.x, size.y, size.z).mod('%')
        bbox.move_to(center=self.center)
        self.obj += bbox.obj

    def translate(self, x=0, y=0, z=0):
        self.anchors.translate(Vector(x, y, z))
        self.obj = solid.translate([x, y, z])(self.obj)
        return self
    tr = translate

    def scale(self, x=1, y=1, z=1):
        self.invalidate_anchors()
        self.obj = solid.scale([x, y, z])(self.obj)
        return self
    sc = scale

    def rotate(self, x=0, y=0, z=0, v=None):
        self.invalidate_anchors()
        self.obj = solid.rotate([x, y, z], v)(self.obj)
        return self
    rot = rotate

    def resize(self, x=0, y=0, z=0, auto=None):
        self.invalidate_anchors()
        self.obj = solid.resize([x, y, z], auto)(self.obj)
        return self
    rsz = resize

    def color(self, *args, **kwargs):
        self.obj = solid.color(*args, **kwargs)(self.obj)
        return self

    def mod(self, mod='#'):
        """
        Shorthand for set_modifier
        """
        self.obj.set_modifier(mod)
        return self

    def __add__(self, other):
        if not isinstance(other, PySCADObject):
            return NotImplemented
        obj = self.obj + other.obj
        return SCADWrapper(obj)

    def __sub__(self, other):
        if not isinstance(other, PySCADObject):
            return NotImplemented
        obj = self.obj - other.obj
        return SCADWrapper(obj)



class SCADWrapper(PySCADObject):

    def make_obj(self, obj):
        self.obj = obj

class ImportScad:

    def __init__(self, modname):
        self.mod = solid.import_scad(modname)

    def __getattr__(self, name):
        fn = getattr(self.mod, name)
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            obj = fn(*args, **kwargs)
            return SCADWrapper(obj)
        return wrapper



class Cube(PySCADObject):
    """
    Like the builtin openscad cube(), but with saner default.

    By default the cube is centered in the origin, and defines the following
    anchor points:

    - center
    - pmin, pmax
    - left, right
    - back, front
    - bottom, top
    """

    def make_obj(self, sx, sy, sz):
        pmin = Point(-sx/2, -sy/2, -sz/2)
        pmax = Point(sx/2, sy/2, sz/2)
        self.obj = solid.cube([sx, sy, sz])
        self.translate(-sx/2, -sy/2, -sz/2)
        self.anchors.set_bounding_box(pmin, pmax)
        self.anchors.center = Point.O

def _get_r_d(r, d):
    if d is None:
        assert r is not None
        d = r*2
    elif r is None:
        assert d is not None
        r = d/2
    else:
        raise ValueError('You must specify r or d')
    return r, d

class Sphere(PySCADObject):

    def make_obj(self, r=None, d=None):
        r, d = _get_r_d(r, d)
        pmin = Point(-r, -r, -r)
        pmax = Point(r, r, r)
        self.anchors.set_bounding_box(pmin, pmax)
        self.anchors.center = Point.O
        self.obj = solid.sphere(d=d)

class Cylinder(PySCADObject):
    """
    Like the builtin opensca cylinder(), but with saner default.

    By default the cylinder is center in the origin, and defines the following
    anchor points:

    - center
    - pmin, pmax
    - left, right
    - back, front
    - bottom, top

    You can specify only r or d. If you want a truncated cone, you
    TruncatedCone().
    """

    def make_obj(self, *, h=None, r=None, d=None, segments=None):
        assert h is not None
        r, d = _get_r_d(r, d)
        pmin = Point(-r, -r, -h/2)
        pmax = Point(r, r, h/2)
        self.anchors.set_bounding_box(pmin, pmax)
        self.anchors.center = Point.O
        self.obj = solid.cylinder(h=h, d=d, center=True, segments=segments)

## class TruncatedCone(PySCADObject):

##     def make_obj(self, *, h=None, r1=None, r2=None, d1=None, d2=None, segments=None):
##         ...


def bolt_hole(*, d, h, clearance=0.2, center=None):
    h = h + EPSILON*2
    cyl = Cylinder(d=d+clearance, h=h, center=center)
    if not center:
        cyl = cyl.translate(z=-EPSILON)
    return cyl


class Preview(PySCADObject):
    """
    Make it possible to render two different things depending on the value of $preview.
    Override the preview() and render() methods for your needs.
    """

    def make_obj(self):
        preview_obj = self.preview()
        render_obj = self.render()
        self.obj = _PreviewObject(preview_obj, render_obj)

    def preview(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class _PreviewObject:

    def __init__(self, preview, render):
        self._preview_obj = preview.obj
        self._render_obj = render.obj
        self.children = self._preview_obj.children + self._render_obj.children
        self.params = {}
        self.params.update(self._preview_obj.params)
        self.params.update(self._render_obj.params)

    def _render(self):
        lines = []
        w = lines.append
        w('if ($preview) {')
        if self._preview_obj:
            w(self._preview_obj._render())
        w('} else {')
        if self._render_obj:
            w(self._render_obj._render())
        w('}')
        return '\n'.join(lines)
