
class Person:
    def __init__(self, name):
        self.name = name


class Employee(Person):
    def get_salary(self):
        return 50000

    def assign_task(self, task):
        print(f"Task assigned: {task}")


class Student(Person):
    def study(self):
        print(f"{self.name} is studying")


def process_employee(employee):
    print("Salary:", employee.get_salary())
    employee.assign_task("Complete the report")


# Main call
if __name__ == "__main__":
    employee = Employee("Ali")
    student = Student("Ahmed")

    process_employee(employee)
    student.study()
