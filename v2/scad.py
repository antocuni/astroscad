import solid
EPSILON = 0.001

def in2mm(inches):
    return inches * 25.4

class ExtraMethods:
    def translate(self, x=0, y=0, z=0):
        return solid.translate([x, y, z])(self)
    tr = translate

    def scale(self, x=0, y=0, z=0):
        return solid.scale([x, y, z])(self)
    sc = scale

    def rotate(self, x=0, y=0, z=0, v=None):
        return solid.rotate([x, y, z], v)(self)
    rot = rotate

    def resize(self, x=0, y=0, z=0, auto=None):
        return solid.resize([x, y, z], auto)(self)
    rsz = resize

    def color(self, *args, **kwargs):
        return solid.color(*args, **kwargs)(self)

    def m(self, mod='#'):
        """
        Shorthand for set_modifier
        """
        return self.set_modifier(mod)

    @classmethod
    def attach_to(cls, target):
        for name, val in cls.__dict__.items():
            if name != 'attach_to' and not name.startswith('__'):
                assert not hasattr(target, name)
                setattr(target, name, val)

ExtraMethods.attach_to(solid.OpenSCADObject)


def _get_st(axis, size, center):
    assert axis in ('x', 'y', 'z')
    t = 0
    if size < 0:
        size = -size
        t = -size
    if axis in center:
        t = -size/2
    return size, t

def _process_center(center):
    assert center in ('', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', True, False)
    if center is True:
        return 'xyz'
    if center is False:
        return ''
    return center


def cube(sx, sy, sz, center=''):
    center = _process_center(center)
    sx, tx = _get_st('x', sx, center)
    sy, ty = _get_st('y', sy, center)
    sz, tz = _get_st('z', sz, center)
    return solid.cube([sx, sy, sz]).translate(tx, ty, tz)

def cylinder(*, h=None, r=None, d=None, r1=None, r2=None, d1=None, d2=None,
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
    return solid.cylinder(h=h, r=r, d=d, r1=r1, r2=r2, d1=d1, d2=d2,
                          center=center,
                          segments=segments).translate(z=tz)

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
