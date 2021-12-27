import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--dev", action="store_true",
        help="Development mode. Save the screenshot as the new reference image, display the screenshot and the live OpenSCAD view")
