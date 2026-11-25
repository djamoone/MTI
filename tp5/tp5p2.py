from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def erase(self):
        pass


class Circle(Shape, ABC):
    pass


class Square(Shape, ABC):
    pass


class Circle2D(Circle):
    def draw(self):
        print("Circle.draw2D")

    def erase(self):
        print("Circle.erase2D")


class Circle3D(Circle):
    def draw(self):
        print("Circle.draw3D")

    def erase(self):
        print("Circle.erase3D")


class Square2D(Square):
    def draw(self):
        print("Square.draw2D")

    def erase(self):
        print("Square.erase2D")


class Square3D(Square):
    def draw(self):
        print("Square.draw3D")

    def erase(self):
        print("Square.erase3D")


class ShapeFactory(ABC):
    @staticmethod
    @abstractmethod
    def createShape(shape_type: str) -> Shape:
        pass


class ShapeFactory2D(ShapeFactory):
    @staticmethod
    def createShape(shape_type: str) -> Shape:
        if shape_type == "Circle":
            return Circle2D()
        elif shape_type == "Square":
            return Square2D()
        else:
            return None


class ShapeFactory3D(ShapeFactory):
    @staticmethod
    def createShape(shape_type: str) -> Shape:
        if shape_type == "Circle":
            return Circle3D()
        elif shape_type == "Square":
            return Square3D()
        else:
            return None


if __name__ == "__main__":
    print("--- 2D Shapes ---")
    for shape_type in ("Circle", "Square", "Circle", "Square"):
        shape = ShapeFactory2D.createShape(shape_type)
        if shape:
            shape.draw()
            shape.erase()

    print("--- 3D Shapes ---")
    for shape_type in ("Circle", "Square", "Circle", "Square"):
        shape = ShapeFactory3D.createShape(shape_type)
        if shape:
            shape.draw()
            shape.erase()