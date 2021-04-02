import solid

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
    return solid.translate([tx, ty, tz])(
        solid.cube([sx, sy, sz]),
    )
