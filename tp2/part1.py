
from abc import ABC, abstractmethod


# =========================================================
# 1. Abstract class: AcademicElement
# =========================================================

class AcademicElement(ABC):
    """Abstract base class for academic entities."""

    def __init__(self, name, title):
        self.name = name
        self.title = title

        self._WEEKS = 15
        self.coef = 0
        self.credit = 0

        # Workload distribution
        self.hours_lecture = 0
        self.hours_td = 0
        self.hours_tp = 0

    @abstractmethod
    def calculate_average(self):
        """Calculate the academic average."""
        pass

    @abstractmethod
    def calculate_credits(self):
        """Calculate the earned credits."""
        pass


# =========================================================
# 2. Module class
# =========================================================

class Module(AcademicElement):
    """Represents a teaching module."""

    def __init__(
        self,
        name: str = "",
        title: str = "",
        coef: int = 1,
        credit: int = 1,
        hours_lecture: float = 1.5,
        hours_td: float = 0,
        hours_tp: float = 0,
        teaching_mode: str = "In-person",
        continous_percent: int = 40,
        exam_percent: int = 60
    ):
        super().__init__(name, title)

        self.coef = coef
        self.credit = credit

        self.hours_lecture = hours_lecture
        self.hours_td = hours_td
        self.hours_tp = hours_tp

        self.teaching_mode = teaching_mode

        self.evaluation_continous_percent = continous_percent
        self.evaluation_exam_percent = exam_percent

        # Total workload over 15 weeks
        self.total_hours = self._WEEKS * (
            self.hours_lecture
            + self.hours_td
            + self.hours_tp
        )

        # Encapsulated grades
        self._grades = {
            "tp": 0,
            "td": 0,
            "exam": 0
        }

    def set_grade(self, tp=None, td=None, exam=None):
        """Update grades without changing unspecified grades."""

        if tp is not None:
            self._grades["tp"] = tp

        if td is not None:
            self._grades["td"] = td

        if exam is not None:
            self._grades["exam"] = exam

    def summary(self):
        """Return a textual description of the module."""

        return (
            f"Module: {self.title} ({self.name})\n"
            f"Coefficient: {self.coef}, Credits: {self.credit}\n"
            f"Total hours: {self.total_hours}\n"
            f"Lecture: {self.hours_lecture}, "
            f"TD: {self.hours_td}, TP: {self.hours_tp}\n"
            f"Teaching mode: {self.teaching_mode}\n"
            f"Continuous assessment: "
            f"{self.evaluation_continous_percent}%\n"
            f"Exam: {self.evaluation_exam_percent}%"
        )

    def calculate_average(self):
        """Calculate the weighted average of the module."""

        tp = self._grades["tp"]
        td = self._grades["td"]
        exam = self._grades["exam"]

        percent_exam = self.evaluation_exam_percent
        percent_tp = 0
        percent_td = 0

        # Distribute continuous assessment between TP and TD
        if self.hours_tp and self.hours_td:
            percent_tp = self.evaluation_continous_percent / 2
            percent_td = self.evaluation_continous_percent / 2

        elif self.hours_td:
            percent_td = self.evaluation_continous_percent

        elif self.hours_tp:
            percent_tp = self.evaluation_continous_percent

        return (
            tp * percent_tp / 100
            + td * percent_td / 100
            + exam * percent_exam / 100
        )

    def calculate_credits(self):
        """Return all module credits if the average is at least 10."""

        if self.calculate_average() >= 10:
            return self.credit

        return 0


# =========================================================
# 3. Unit class
# =========================================================

class Unit(AcademicElement):
    """Represents a teaching unit containing multiple modules."""

    def __init__(self, name, title, modules=None):
        super().__init__(name, title)

        # Avoid a mutable default argument
        self._modules = list(modules) if modules is not None else []

        # Unit coefficient and total possible credits
        self.coef = sum(module.coef for module in self._modules)
        self.credit = sum(module.credit for module in self._modules)

    def add_module(self, module):
        """Add a module to the unit."""

        if not isinstance(module, Module):
            raise TypeError("A unit can contain only Module objects.")

        self._modules.append(module)

        self.coef += module.coef
        self.credit += module.credit

    def calculate_average(self):
        """Calculate the weighted average of all modules."""

        if not self._modules:
            return 0

        coef_sum = sum(module.coef for module in self._modules)

        if coef_sum == 0:
            return 0

        total = sum(
            module.calculate_average() * module.coef
            for module in self._modules
        )

        return total / coef_sum

    def calculate_credits(self):
        """Calculate credits earned by the unit."""

        if not self._modules:
            return 0

        if self.calculate_average() >= 10:
            return sum(module.credit for module in self._modules)

        return sum(
            module.calculate_credits()
            for module in self._modules
        )


# =========================================================
# 4. Semester class
# =========================================================

class Semester(AcademicElement):
    """Represents a semester containing multiple units."""

    def __init__(self, name, title, units=None):
        super().__init__(name, title)

        self._units = list(units) if units is not None else []

        self.coef = sum(unit.coef for unit in self._units)
        self.credit = sum(unit.credit for unit in self._units)

    def add_unit(self, unit):
        """Add a unit to the semester."""

        if not isinstance(unit, Unit):
            raise TypeError("A semester can contain only Unit objects.")

        self._units.append(unit)

        self.coef += unit.coef
        self.credit += unit.credit

    def calculate_average(self):
        """Calculate the weighted average of all units."""

        if not self._units:
            return 0

        coef_sum = sum(unit.coef for unit in self._units)

        if coef_sum == 0:
            return 0

        total = sum(
            unit.calculate_average() * unit.coef
            for unit in self._units
        )

        return total / coef_sum

    def calculate_credits(self):
        """Calculate the credits earned during the semester."""

        return sum(
            unit.calculate_credits()
            for unit in self._units
        )


# =========================================================
# 5. Main program: Test all classes
# =========================================================

if __name__ == "__main__":

    # Create the first module
    m1 = Module(
        name="MTI",
        title="Methods and Technologies of Implementation",
        coef=3,
        credit=5,
        hours_lecture=1.5,
        hours_tp=1.5,
        teaching_mode="In-person",
        continous_percent=40,
        exam_percent=60
    )

    m1.set_grade(tp=10, exam=12)

    print("MODULE 1")
    print(m1.summary())
    print("Average:", m1.calculate_average())
    print("Credits earned:", m1.calculate_credits())

    print("\n" + "=" * 50 + "\n")

    # Create the second module
    m2 = Module(
        name="AABD",
        title="Database Architecture and Administration",
        coef=2,
        credit=4,
        hours_lecture=1.5,
        hours_tp=1.5,
        teaching_mode="In-person",
        continous_percent=40,
        exam_percent=60
    )

    m2.set_grade(tp=8, exam=6)

    print("MODULE 2")
    print(m2.summary())
    print("Average:", m2.calculate_average())
    print("Credits earned:", m2.calculate_credits())

    print("\n" + "=" * 50 + "\n")

    # Create a unit containing both modules
    u1 = Unit(
        name="UEM11",
        title="UE Methodology",
        modules=[m1, m2]
    )

    print("UNIT")
    print("Unit name:", u1.name)
    print("Unit title:", u1.title)
    print("Unit average:", u1.calculate_average())
    print("Unit credits:", u1.calculate_credits())

    print("\n" + "=" * 50 + "\n")

    # Create a semester containing the unit
    s1 = Semester(
        name="S1",
        title="Semester 1",
        units=[u1]
    )

    print("SEMESTER")
    print("Semester name:", s1.name)
    print("Semester title:", s1.title)
    print("Semester average:", s1.calculate_average())
    print("Semester credits:", s1.calculate_credits())
