import math
from ..scad import ImportScad, PySCADObject, Cylinder, Union, Cube
from ..geometry import Point, Vector, AnchorPoints

_step_motor = ImportScad('vendored/motors/StepMotor_28BYJ-48.scad')


class Stepper_28BYJ48(PySCADObject):
    """
    28-BYJ48 5V Stepper motor:
    https://components101.com/motors/28byj-48-stepper-motor

    The motory BODY has the same anchor points and properties of a cylinder:
    this means that e.g. the motor shaft will be OUTSIDE of the bounding box
    (which is what you usually want, because you want to place the motory body
    against a surface, and let the shaft to protrude from it).
    """

    # copied & pasted from Stepper_28BYJ48.scad

    _MBH = 18.8     # motor body height
    _MBD = 28.25    # motor body OD
    _SBD = 9.1      # shaft boss OD
    _SBH = 1.45     # shaft boss height above motor body
    _SBO = 7.875    # offset of shaft/boss center from motor center
    _SHD = 4.93     # motor shaft OD
    _SHDF = 3.0     # motor shaft diameter, across flats
    _SHHF = 6.0     # motor shaft flats height, or depth in from end
    _SHH = 9.75     # height of shaft above motor body

    _MBFH = 0.7     # height of body edge flange protruding above surface
    _MBFW = 1.0     # width of edge flange
    _MBFNW = 8      # width of notch in edge flange
    _MBFNW2 = 17.8  # width of edge flange notch above wiring box

    _MHCC = 35.0    # mounting hole center-to-center
    _MTH  = 0.8     # mounting tab thickness
    _MTW  = 7.0     # mounting tab width
    _WBH  = 16.7    # plastic wiring box height
    _WBW  = 14.6    # plastic wiring box width
    _WBD  = 31.3    # body diameter to outer surface of wiring box

    _WRD = 1.0      # diameter of electrical wires
    _WRL = 30       # length of electrical wires
    _WRO = 2.2	   # offset of wires below top motor surface


    def init_solid(self):
        # to compute the anchors, we create a thrown-away Cylinder which is
        # "equivalent" to the motor body
        cyl = Cylinder(d=self._MBD, h=self._MBH, axis='x')
        self.anchors.center = Point.O
        self.anchors.set_bounding_box(cyl.pmin, cyl.pmax)
        # add a anchor for the shaft
        self.anchors.shaft = Point(None, 0, self._SBO)
        #
        # create the motor and rotate so that the shaft is parallel to the 'x' axis
        _stepper = _step_motor.StepMotor28BYJ()
        _stepper.rotate(0, -90, 0)
        #
        # _stepper is a GenericSCADWrapper, manually unwrap it
        self.solid = _stepper.solid
