from academicelement import AcademicElement
from module import Module


class Unit(AcademicElement):
    def __init__(self, name, title):
        super().__init__(name, title)

        self._modules = []
        self.coef = 0

    def add_module(self, module):
        if not isinstance(module, Module):
            raise TypeError("A Unit can contain only Module objects")

        self._modules.append(module)
        self.coef += module.coef

    def calculate_average(self):
        """Example of aggregation — combining module averages."""
        if not self._modules:
            return 0

        total = 0
        coef_sum = 0

        for m in self._modules:
            avg = m.calculate_average()

            # If any module has no average yet, the unit average
            # cannot be computed either (consistent with Semester).
            if avg is None:
                return None

            total += avg * m.coef
            coef_sum += m.coef

        if coef_sum == 0:
            return 0

        return total / coef_sum

    def calculate_credits(self):
        """Polymorphism: different modules could override this behavior."""
        if not self._modules:
            return 0

        avg = self.calculate_average()

        # If the unit average cannot be computed (some module has no
        # grade yet), fall back to counting only the modules that
        # individually passed instead of crashing.
        if avg is None:
            return sum(m.calculate_credits() for m in self._modules)

        if avg >= 10:
            # Compensation: the unit is passed as a whole, so every
            # module in it is validated.
            total_credits = sum(m.credit for m in self._modules)
        else:
            # No compensation: only modules passed individually count.
            total_credits = sum(m.calculate_credits() for m in self._modules)

        return total_credits