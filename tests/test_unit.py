import sys
import os

# Add the parent folder (gsi_project) to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module import Module
from unit import Unit


def test_unit_average():
    m1 = Module(
        "MTI", "Methods",
        coef=3, credit=5, hours_tp=1.5
    )
    m1.set_grade(tp=10, exam=12)

    m2 = Module(
        "AABD", "Databases",
        coef=2, credit=4, hours_tp=1.5
    )
    m2.set_grade(tp=8, exam=6)

    unit = Unit("U1", "Unit 1")
    unit.add_module(m1)
    unit.add_module(m2)

    assert abs(unit.calculate_average() - 9.44) < 0.0001
    assert unit.calculate_credits() == 5


def test_empty_unit():
    unit = Unit("U1", "Unit 1")

    assert unit.calculate_average() == 0
    assert unit.calculate_credits() == 0


if __name__ == "__main__":
    test_unit_average()
    test_empty_unit()
    print("All tests passed!")