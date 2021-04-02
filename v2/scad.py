import solid

class ExtraMethods:
    def translate(self, x=0, y=0, z=0):
        return solid.translate([x, y, z])(self)

    def scale(self, x=0, y=0, z=0):
        return solid.scale([x, y, z])(self)

    def rotate(self, x=0, y=0, z=0, v=None):
        return solid.rotate([x, y, z], v)(self)

    def resize(self, x=0, y=0, z=0, auto=None):
        return solid.resize([x, y, z], auto)(self)

    def color(self, *args, **kwargs):
        return solid.color(*args, **kwargs)(self)

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
