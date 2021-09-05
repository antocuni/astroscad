import solid
EPSILON = 0.001

def in2mm(inches):
    return inches * 25.4

## class BoundingBox:
##     def __init__(self, x0, y0, z0, x1, y1, z1):
##         self.x0, self.x1 = sorted((x0, x1))
##         self.y0, self.y1 = sorted((y0, y1))
##         self.z0, self.z1 = sorted((z0, z1))


class MySCADObject:
    """
    This is a wrapper around solid.OpenSCADObject, so that we can add our own
    functionalities
    """

    def __init__(self, *args, **kwargs):
        # these two attributes are unused but are required to mock a real
        # OpenSCADObject
        self.children = []
        self.params = {}
        self.obj = None
        self.make_obj(*args, **kwargs)
        assert self.obj is not None

    @classmethod
    def wrap(self, obj):
        return SCADWrapper(obj)

    def make_obj(self, *args, **kwargs):
        raise NotImplementedError

    def _render(self, render_holes=False):
        return self.obj._render(render_holes=render_holes)

    # helper methods
    def translate(self, x=0, y=0, z=0):
        self.obj = solid.translate([x, y, z])(self.obj)
        return self
    tr = translate

    def scale(self, x=1, y=1, z=1):
        self.obj = solid.scale([x, y, z])(self.obj)
        return self
    sc = scale

    def rotate(self, x=0, y=0, z=0, v=None):
        self.obj = solid.rotate([x, y, z], v)(self.obj)
        return self
    rot = rotate

    def resize(self, x=0, y=0, z=0, auto=None):
        self.obj = solid.resize([x, y, z], auto)(self.obj)
        return self
    rsz = resize

    def color(self, *args, **kwargs):
        self.obj = solid.color(*args, **kwargs)(self.obj)
        return self

    def m(self, mod='#'):
        """
        Shorthand for set_modifier
        """
        self.obj.set_modifier(mod)
        return self

    def __add__(self, other):
        if not isinstance(other, MySCADObject):
            return NotImplemented
        obj = self.obj + other.obj
        return self.wrap(obj)

    def __sub__(self, other):
        if not isinstance(other, MySCADObject):
            return NotImplemented
        obj = self.obj - other.obj
        return self.wrap(obj)



class SCADWrapper(MySCADObject):

    def make_obj(self, obj):
        self.obj = obj


class Cube(MySCADObject):

    def make_obj(self, sx, sy, sz, center=''):
        center = self._process_center(center)
        sx, tx = self._get_st('x', sx, center)
        sy, ty = self._get_st('y', sy, center)
        sz, tz = self._get_st('z', sz, center)
        self.obj = solid.cube([sx, sy, sz])
        self.translate(tx, ty, tz)

    def _process_center(self, center):
        assert center in ('', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', True, False)
        if center is True:
            return 'xyz'
        if center is False:
            return ''
        return center

    def _get_st(self, axis, size, center):
        """
        Get the size and translation for a given axis
        """
        assert axis in ('x', 'y', 'z')
        t = 0
        if size < 0:
            size = -size
            t = -size
        if axis in center:
            t = -size/2
        return size, t


class Cylinder(MySCADObject):

    def make_obj(self, *, h=None, r=None, d=None, r1=None, r2=None, d1=None, d2=None,
                 center=None, segments=None):
        if r is not None:
            assert r1 is None, 'Cannot use r1 together with r'
            assert r2 is None, 'Cannot use r2 together with r'
            assert d is None, 'Cannot use d together with r'
            assert d1 is None, 'Cannot use d1 together with r'
            assert d2 is None, 'Cannot use d2 together with r'
        elif r1 is not None or r2 is not None:
            assert d is None, 'Cannot use d together with r'
            assert d1 is None, 'Cannot use d1 together with r'
            assert d2 is None, 'Cannot use d2 together with r'
        elif d is not None:
            assert d1 is None, 'Cannot use d1 together with r'
            assert d2 is None, 'Cannot use d2 together with r'
        else:
            assert d1 is not None or d2 is not None, \
                'You must specify one of r, d, r1, r2, d1, d2'
        #
        tz = 0
        if h < 0:
            h = -h
            tz = -h
            r1, r2 = r2, r1
            d1, d2 = d2, d1
        self.obj = solid.cylinder(h=h, r=r, d=d, r1=r1, r2=r2, d1=d1, d2=d2,
                                  center=center,
                                  segments=segments)
        self.translate(z=tz)

def render_to_file(*args, fn=None, fa=None, fs=None, **kwargs):
    header = []
    if fn: header.append(f'$fn = {fn};')
    if fa: header.append(f'$fa = {fa};')
    if fs: header.append(f'$fs = {fs};')
    header = '\n'.join(header)
    return solid.scad_render_to_file(*args, file_header=header, **kwargs)


def bolt_hole(*, d, h, clearance=0.2, center=None):
    h = h + EPSILON*2
    cyl = cylinder(d=d+clearance, h=h, center=center)
    if not center:
        cyl = cyl.translate(z=-EPSILON)
    return cyl


class Preview:
    """
    Make it possible to render two different things depending on the value of $preview.
    Override the preview() and render() methods for your needs.
    """

    def __init__(self):
        self._preview_obj = self.preview()
        self._render_obj = self.render()
        self.children = []
        self.params = {}
        if self._preview_obj:
            self.children += self._preview_obj.children
            self.params.update(self._preview_obj.params)
        if self._render_obj:
            self.children += self._render_obj.children
            self.params.update(self._render_obj.params)

    def preview(self):
        return None

    def render(self):
        return None

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
