import solid

def cube(sx, sy, sz, center=''):
    assert center in ('', 'x', 'y', 'z', 'xy', 'xz', 'yz', 'xyz', True, False)
    if center is True:
        center = 'xyz'
    if center is False:
        center = ''

    tx, ty, tz = 0, 0, 0
    if center == 'xyz':
        return solid.cube([sx, sy, sz], center=True)

    if 'x' in center:
        tx = -sx/2
    if 'y' in center:
        ty = -sy/2
    if 'z' in center:
        tz = -sz/2

    return solid.translate([tx, ty, tz])(
        solid.cube([sx, sy, sz]),
    )
