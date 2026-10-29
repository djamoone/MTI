from academicelement import AcademicElement
from unit import Unit


class Semester(AcademicElement):
    def __init__(self, name, title):
        super().__init__(name, title)

        self.units = []
        self.coef = 0

    def add_unit(self, unit):
        if not isinstance(unit, Unit):
            raise TypeError("A Semester can contain only Unit objects")

        self.units.append(unit)
        self.coef += unit.coef

    def calculate_average(self):
        if len(self.units) == 0:
            return 0

        total = 0
        total_coef = 0

        for unit in self.units:
            average = unit.calculate_average()

            if average is None:
                return None

            total += average * unit.coef
            total_coef += unit.coef

        if total_coef == 0:
            return 0

        return total / total_coef

    def calculate_credits(self):
        total_credits = 0

        for unit in self.units:
            total_credits += unit.calculate_credits()

        return total_credits