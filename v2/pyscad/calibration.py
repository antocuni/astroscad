# These are calibration parameters which work for my current setup:
#   - Ender 3 Pro
#   - PLA
#   - current calibration settings

# In the future, we need to make it possible to configure these params in a
# better way

class CalibrationData:

    BEARING_HOLE_CLEARANCE = {
        '604': 0.5,
        '608': 0.7,
    }

    TEFLON_GLIDE_GROOVE_CLEARANCE = 0.8

    MANFROTTO_RUBBER_PAD_CLEARANCE = (0.5, 0.5, 0) # x, y, z
