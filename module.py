from academicelement import AcademicElement


class Module(AcademicElement):
    def __init__(
        self,
        name="",
        title="",
        coef=1,
        credit=1,
        hours_lecture=1.5,
        hours_td=0,
        hours_tp=0,
        teaching_mode="In-person",
        continous_percent=40,
        exam_percent=60
    ):
        super().__init__(name, title)

        self.coef = coef
        self.credit = credit

        self.hours_lecture = hours_lecture
        self.hours_td = hours_td
        self.hours_tp = hours_tp

        self.teaching_mode = teaching_mode
        self.continous_percent = continous_percent
        self.exam_percent = exam_percent

        self.total_hours = self.weeks * (
            self.hours_lecture
            + self.hours_td
            + self.hours_tp
        )

        self._grades = {
            "tp": None,
            "td": None,
            "exam": None
        }

    def set_grade(self, tp=None, td=None, exam=None):
        if tp is not None:
            if tp < 0 or tp > 20:
                raise ValueError("TP grade must be between 0 and 20")
            self._grades["tp"] = tp

        if td is not None:
            if td < 0 or td > 20:
                raise ValueError("TD grade must be between 0 and 20")
            self._grades["td"] = td

        if exam is not None:
            if exam < 0 or exam > 20:
                raise ValueError("Exam grade must be between 0 and 20")
            self._grades["exam"] = exam

    def summary(self):
        print("Module:", self.title)
        print("Code:", self.name)
        print("Coefficient:", self.coef)
        print("Credits:", self.credit)
        print("Total hours:", self.total_hours)
        print("Teaching mode:", self.teaching_mode)

    def calculate_average(self):
        tp = self._grades["tp"]
        td = self._grades["td"]
        exam = self._grades["exam"]

        if exam is None:
            return None

        has_tp = tp is not None
        has_td = td is not None

        # Determine the weighting based on which continuous-assessment
        # grades are actually set (not on declared hours), so the
        # average is always normalized to 100%.
        if has_tp and has_td:
            percent_tp = self.continous_percent / 2
            percent_td = self.continous_percent / 2
            percent_exam = self.exam_percent
        elif has_tp:
            percent_tp = self.continous_percent
            percent_td = 0
            percent_exam = self.exam_percent
        elif has_td:
            percent_tp = 0
            percent_td = self.continous_percent
            percent_exam = self.exam_percent
        else:
            # No continuous assessment -> the exam counts for 100%.
            percent_tp = 0
            percent_td = 0
            percent_exam = 100

        average = 0

        if has_tp:
            average += tp * percent_tp / 100

        if has_td:
            average += td * percent_td / 100

        average += exam * percent_exam / 100

        return average

    def calculate_credits(self):
        average = self.calculate_average()

        if average is not None and average >= 10:
            return self.credit

        return 0


