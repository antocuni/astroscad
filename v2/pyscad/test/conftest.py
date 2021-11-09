import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--save-ref-img", action="store_true",
        help="Save the screenshots produced by OpenSCAD as the new reference images")
    parser.addoption(
        "--show-scad", action="store_true",
        help="Open the rendered scad file in openscad")
