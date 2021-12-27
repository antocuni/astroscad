"""
Naming convention:

  - 'objects' are the high-level instances of PySCADObject subclasses

  - 'solids' are the low-level solidpython primitives (e.g. solid.cube or
    solid.union)
"""

import os
from pathlib import Path
import functools

import solid
from .geometry import Point, Vector, AnchorPoints
from .camera import Camera
from .util import InvalidAnchorPoints, render_to_collage
from .autorender import autorender

EPS = 0.001

os.environ['OPENSCADPATH'] = ':'.join([
    '/usr/share/openscad/libraries/',
    str(Path(__file__).parent),
])

class PySCADObject:
    """
    This is a wrapper around solid.OpenSCADObject, so that we can add our own
    functionalities
    """

    def __init__(self, *args, **kwargs):
        self.anchors = AnchorPoints()
        self.children = []
        self.solid = None
        self.init_solid(*args, **kwargs)
        assert self.solid is not None

    def init_solid(self, *args, **kwargs):
        raise NotImplementedError

    def autorender(self, *, filename='/tmp/autorender.scad', **kwargs):
        autorender(self, filename, **kwargs)

    def render_to_file(self, filename, *, fa=1, fs=0.4, fn=None):
        header = []
        if fn: header.append(f'$fn = {fn};')
        if fa: header.append(f'$fa = {fa};')
        if fs: header.append(f'$fs = {fs};')
        header = '\n'.join(header)
        return solid.scad_render_to_file(self.solid, filename, file_header=header)

    def render_to_image(self, filename, camera=Camera.DEFAULT, size=(512, 512),
                        **kwargs):
        png = Path(filename)
        scad = png.with_suffix('.scad')
        self.render_to_file(scad, **kwargs)
        cam = camera.as_cmdline()
        sx, sy = size
        view = 'axes'
        ret = os.system(f'openscad "{scad}" -o "{png}" '
                        f'--camera {cam} '
                        f'--imgsize {sx},{sy} '
                        f'--view {view}')
        if ret != 0:
            raise ValueError(ret)

    def render_to_collage(self, filename, distance=None):
        render_to_collage(self, filename, distance)

    def __getattr__(self, name):
        if self.anchors.has_point(name):
            return getattr(self.anchors, name)
        raise AttributeError(name)

    def invalidate_anchors(self):
        self.anchors = InvalidAnchorPoints(self.anchors)

    def _all_anchors(self):
        yield self.anchors
        for child in self.children:
            assert isinstance(child, PySCADObject)
            yield from child._all_anchors()

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
        bbox.move_to(pmin=self.pmin)
        self.solid += bbox.solid
        return self

    def translate(self, x=0, y=0, z=0):
        for anchors in self._all_anchors():
            anchors.translate(Vector(x, y, z))
        self.solid = solid.translate([x, y, z])(self.solid)
        return self
    tr = translate

    def scale(self, x=1, y=1, z=1):
        self.invalidate_anchors()
        self.solid = solid.scale([x, y, z])(self.solid)
        return self
    sc = scale

    def rotate(self, x=0, y=0, z=0, v=None):
        self.invalidate_anchors()
        self.solid = solid.rotate([x, y, z], v)(self.solid)
        return self
    rot = rotate

    def resize(self, x=0, y=0, z=0, auto=None):
        self.invalidate_anchors()
        self.solid = solid.resize([x, y, z], auto)(self.solid)
        return self
    rsz = resize

    def color(self, *args, **kwargs):
        self.solid = solid.color(*args, **kwargs)(self.solid)
        return self

    def mod(self, mod='#'):
        """
        Shorthand for set_modifier
        """
        self.solid.set_modifier(mod)
        return self

    def __neg__(self):
        return Neg(self)

    def __add__(self, other):
        if isinstance(other, PySCADObject):
            return Union(self, other)
        elif isinstance(other, Neg):
            return self - other.x
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, PySCADObject):
            self.children.append(other)
            self.solid += other.solid
            return self
        elif isinstance(other, Neg):
            self -= other.x
            return self
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, PySCADObject):
            return NotImplemented
        return Difference(self, other)

    def __isub__(self, other):
        if not isinstance(other, PySCADObject):
            return NotImplemented
        self.children.append(other)
        self.solid -= other.solid
        return self

    def __imul__(self, other):
        if not isinstance(other, PySCADObject):
            return NotImplemented
        self.children.append(other)
        self.solid *= other.solid
        return self

class Neg:

    def __init__(self, x):
        self.x = x



class Union(PySCADObject):

    def init_solid(self, *objs):
        self.solid = solid.union()
        for obj in objs:
            self += obj

class Difference(PySCADObject):

    def init_solid(self, *objs):
        # note: the solid.union() below is not a mistake, it's just used to
        # make an empty object. The actual solid.difference() is created by
        # the -= operator.
        # Note that it works because when doing a difference(), OpenSCAD
        # ignores all the "empty objects" before the first non-empty one.
        self.solid = solid.union()
        for obj in objs:
            self -= obj


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

    def init_solid(self, sx, sy=None, sz=None):
        if sy is None:
            sy = sx
        if sz is None:
            sz = sx
        pmin = Point(-sx/2, -sy/2, -sz/2)
        pmax = Point(sx/2, sy/2, sz/2)
        self.solid = solid.cube([sx, sy, sz], center=True)
        self.anchors.set_bounding_box(pmin, pmax)
        assert self.anchors.center == Point.O
        self.size = Vector(sx, sy, sz)

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

    def init_solid(self, *, r=None, d=None):
        r, d = _get_r_d(r, d)
        self.r = r
        self.d = d
        pmin = Point(-r, -r, -r)
        pmax = Point(r, r, r)
        self.anchors.set_bounding_box(pmin, pmax)
        assert self.anchors.center == Point.O
        self.solid = solid.sphere(d=d)

class Cylinder(PySCADObject):
    """
    Similar to the builtin openscad cylinder(), but with saner default.

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

    def init_solid(self, *, h, axis='z', r=None, d=None, segments=None):
        # parse the radius
        r, d = _get_r_d(r, d)
        self.r = r
        self.d = d
        self._init_cylinder(h, axis, r, r, segments)

    def _init_cylinder(self, h, axis, r1, r2, segments):
        assert axis in ('x', 'y', 'z')
        self.h = h
        self.axis = axis
        R = max(r1, r2)
        if axis == 'z':
            pmin = Point(-R, -R, -h/2)
            pmax = Point( R,  R,  h/2)
            self.rot_vector = [0, 0, 0]
        elif axis == 'x':
            pmin = Point(-h/2, -R, -R)
            pmax = Point( h/2,  R,  R)
            self.rot_vector = [0, 90, 0]
        elif axis == 'y':
            pmin = Point(-R, -h/2, -R)
            pmax = Point( R,  h/2,  R)
            self.rot_vector = [-90, 0, 0]
        else:
            assert False

        self.anchors.set_bounding_box(pmin, pmax)
        assert self.anchors.center == Point.O
        self.solid = solid.rotate(self.rot_vector)(
            solid.cylinder(h=h, r1=r1, r2=r2, center=True, segments=segments)
        )


class TCone(Cylinder):
    """
    Truncated cone
    """

    def init_solid(self, *, h, axis='z',
                   r1=None, r2=None, d1=None, d2=None,
                   segments=None):
        self.r1, self.d1 = _get_r_d(r1, d1)
        self.r2, self.d2 = _get_r_d(r2, d2)
        self._init_cylinder(h, axis, self.r1, self.r2, segments)


class CustomObject(PySCADObject):
    """
    Base class for custom objects which are implemented in terms of other
    high-level PySCADObject (i.e., *without* messing with self.solid)
    """

    def init_solid(self, *args, **kwargs):
        self.solid = solid.union()
        self.init_custom(*args, **kwargs)

    def init_custom(self):
        pass

    def __setattr__(self, name, obj):
        if isinstance(obj, PySCADObject):
            self += obj
        elif isinstance(obj, list):
            # this is a bit of a hack, we need to think more about this
            for item in obj:
                if isinstance(item, PySCADObject):
                    self += item
        super().__setattr__(name, obj)

    def add(self, **kwargs):
        for name, obj in kwargs.items():
            if not isinstance(obj, PySCADObject):
                raise TypeError
            setattr(self, name, obj) # this automatically does the +=

    def sub(self, **kwargs):
        for name, obj in kwargs.items():
            if not isinstance(obj, PySCADObject):
                raise TypeError
            object.__setattr__(self, name, obj)
            self -= obj

def bolt_hole(*, d, h, clearance=0.2):
    h = h + EPS*2
    cyl = Cylinder(d=d+clearance, h=h)
    return cyl


class Preview(PySCADObject):
    """
    Make it possible to render two different things depending on the value of $preview.
    Override the preview() and render() methods for your needs.
    """

    def init_solid(self):
        preview_obj = self.preview()
        render_obj = self.render()
        self.solid = _PreviewSolid(preview_obj, render_obj)

    def preview(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError


class _PreviewSolid:

    def __init__(self, preview_obj, render_obj):
        self._preview_solid = preview_obj.solid
        self._render_solid = render_obj.solid
        self.children = self._preview_solid.children + self._render_solid.children
        self.params = {}
        self.params.update(self._preview_solid.params)
        self.params.update(self._render_solid.params)

    def _render(self):
        lines = []
        w = lines.append
        w('if ($preview) {')
        if self._preview_solid:
            w(self._preview_solid._render())
        w('} else {')
        if self._render_solid:
            w(self._render_solid._render())
        w('}')
        return '\n'.join(lines)



class ImportScad:

    def __init__(self, modname):
        self.mod = solid.import_scad(modname)

    def __getattr__(self, name):
        fn = getattr(self.mod, name)
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            obj = fn(*args, **kwargs)
            return GenericSCADWrapper(obj)
        return wrapper

class GenericSCADWrapper(PySCADObject):

    def init_solid(self, obj):
        self.solid = obj
