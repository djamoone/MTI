import sys
import os

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from module import Module
from unit import Unit
from semester import Semester


def test_semester_average():
    module = Module(
        "MTI", "Methods",
        coef=3, credit=5, hours_tp=1.5
    )
    module.set_grade(tp=10, exam=12)

    unit = Unit("U1", "Unit 1")
    unit.add_module(module)

    semester = Semester("S1", "Semester 1")
    semester.add_unit(unit)

    assert abs(semester.calculate_average() - 11.2) < 0.0001
    assert semester.calculate_credits() == 5
    