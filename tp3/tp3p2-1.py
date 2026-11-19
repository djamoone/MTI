# class Rectangle:
#     def set_width(self, width):
#         self.width = width
#     def set_height(self, height):
#         self.height = height
#     def get_area(self):
#         return self.width * self.height
# class Square(Rectangle): # Square inherits from Rectangle
#     def set_width(self, width):
#         self.width = width
#         self.height = width # Enforces width == height
#     def set_height(self, height):
#         self.height = height
#         self.width = height # Enforces width == height

# # Client code that expects a Rectangle
# def print_area(rectangle):
#     print(f"Area: {rectangle.get_area()}")


# After applying LSP (correct design)
class Shape:
    def get_area(self):
        raise NotImplementedError("Must be implemented by the subclass")
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def get_area(self):
        return self.width * self.height


class Square(Shape):
    def __init__(self, side_length):
        self.side_length = side_length
    def get_area(self):
        return self.side_length * self.side_length
# Client code that expects a Shape
def print_area(shape):
    print(f"Area: {shape.get_area()}")

if __name__ == '__main__':
    # Creating a rectangle and a square
    rect = Rectangle(5,10)
    # rect.set_width(5)
    # rect.set_height(10)
    square = Square(5)
    # square.side_length(5)
    print_area(rect) # Works fine
    print_area(square) # This will produce incorrect results due to violation of LSP