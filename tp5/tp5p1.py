import sys


class Shape:
    def draw(self):
        raise NotImplementedError

    def erase(self):
        raise NotImplementedError


class Circle(Shape):
    def draw(self):
        print("Circle.draw")

    def erase(self):
        print("Circle.erase")


class Square(Shape):
    def draw(self):
        print("Square.draw")

    def erase(self):
        print("Square.erase")


class Triangle(Shape):
    def draw(self):
        print("Triangle.draw")

    def erase(self):
        print("Triangle.erase")


class Rectangle(Shape):
    def draw(self):
        print("Rectangle.draw")

    def erase(self):
        print("Rectangle.erase")


class ShapeFactory:
    @staticmethod
    def createShape(shape_type):
        raise NotImplementedError


# Squares, Circles, and Triangles only
class ShapeFactory_SCT(ShapeFactory):
    @staticmethod
    def createShape(shape_type):
        if shape_type == "Square":
            return Square()
        elif shape_type == "Circle":
            return Circle()
        elif shape_type == "Triangle":
            return Triangle()
        else:
            print(f"ShapeFactory_SCT cannot create: {shape_type}")
            sys.exit(1)


# Squares, Circles, and Rectangles only
class ShapeFactory_SCR(ShapeFactory):
    @staticmethod
    def createShape(shape_type):
        if shape_type == "Square":
            return Square()
        elif shape_type == "Circle":
            return Circle()
        elif shape_type == "Rectangle":
            return Rectangle()
        else:
            print(f"ShapeFactory_SCR cannot create: {shape_type}")
            sys.exit(1)


if __name__ == "__main__":
    print("--- SCT Factory ---")
    for t in ("Square", "Circle", "Triangle"):
        s = ShapeFactory_SCT.createShape(t)
        s.draw()
        s.erase()

    print("--- SCR Factory ---")
    for t in ("Square", "Circle", "Rectangle"):
        s = ShapeFactory_SCR.createShape(t)
        s.draw()
        s.erase()