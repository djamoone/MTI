import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module import Module


def test_module_average():
    module = Module(
        "MTI",
        "Methods and Technologies",
        coef=3,
        credit=5,
        hours_tp=1.5
    )

    module.set_grade(tp=10, exam=12)

    assert module.calculate_average() == 11.2
    assert module.calculate_credits() == 5


def test_module_failed():
    module = Module(
        "AABD",
        "Database Architecture",
        coef=2,
        credit=4,
        hours_tp=1.5
    )

    module.set_grade(tp=8, exam=6)

    assert abs(module.calculate_average() - 6.8) < 0.0001
    assert module.calculate_credits() == 0


def test_missing_exam():
    module = Module("MTI", "Methods", hours_tp=1.5)
    module.set_grade(tp=10)

    assert module.calculate_average() is None
    assert module.calculate_credits() == 0


if __name__ == "__main__":
    test_module_average()
    test_module_failed()
    test_missing_exam()
    print("All tests passed!")