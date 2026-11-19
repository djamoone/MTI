

class Teaching:
    def teach(self):
        pass


class Research:
    def conduct_research(self):
        pass


class Medicine:
    def practice_medicine(self):
        pass



class ProfessorResearcher(Teaching, Research):

    def teach(self):
        print("Professor is teaching students.")

    def conduct_research(self):
        print("Professor is conducting scientific research.")


class FullTimeResearcher(Research):

    def conduct_research(self):
        print("Full-time researcher is conducting scientific research.")


class ProfessorHospitalResearcher(Teaching, Research, Medicine):

    def teach(self):
        print("Hospital professor is teaching students.")

    def conduct_research(self):
        print("Hospital professor is conducting medical research.")

    def practice_medicine(self):
        print("Hospital professor is practicing medicine.")


if __name__ == "__main__":

    professor = ProfessorResearcher()
    researcher = FullTimeResearcher()
    hospital_professor = ProfessorHospitalResearcher()

    print("=== Professor Researcher ===")
    professor.teach()
    professor.conduct_research()

    print("\n=== Full-time Researcher ===")
    researcher.conduct_research()

    print("\n=== Professor Hospital Researcher ===")
    hospital_professor.practice_medicine()
    hospital_professor.teach()
    hospital_professor.conduct_research()