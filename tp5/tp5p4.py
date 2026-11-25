from abc import ABC, abstractmethod


# ==========================================
# Parts 1–4: Story Builder
# ==========================================
class Story:
    """Represent the complex object under construction."""

    def __init__(self):
        self.parts = []

    def add(self, part):
        self.parts.append(part)

    def show(self):
        print(self.parts)


class Builder(ABC):
    """Specify an abstract interface for creating parts of a Product object."""

    def __init__(self):
        self.story = Story()

    @abstractmethod
    def _build_image(self):
        pass

    @abstractmethod
    def _build_music(self):
        pass

    @abstractmethod
    def _build_effet(self):
        pass

    @abstractmethod
    def _build_video(self):
        pass


class StoryDirector:
    """Construct an object using the Builder interface."""

    def __init__(self):
        self._builder = None

    def construct(self, builder: Builder):
        self._builder = builder

    def basic_story(self):
        print("*** create basic story ***")
        self._builder._build_image()

    def photo_music_story(self):
        print("*** create photo + music story ***")
        self._builder._build_image()
        self._builder._build_music()
        self._builder._build_effet()

    def video_story(self):
        print("*** create video story ***")
        self._builder._build_video()
        self._builder._build_effet()


class FacebookConcreteBuilder(Builder):
    def _build_image(self):
        self.story.add("image facebook")

    def _build_music(self):
        self.story.add("music facebook")

    def _build_effet(self):
        self.story.add("effect facebook")

    def _build_video(self):
        self.story.add("video facebook")


class InstagramConcreteBuilder(Builder):
    def _build_image(self):
        self.story.add("image Instagram")

    def _build_music(self):
        self.story.add("music Instagram")

    def _build_effet(self):
        self.story.add("effect Instagram")

    def _build_video(self):
        self.story.add("video Instagram")


def run_story_builder():
    print("=== Story Builder ===")
    concrete_builder = FacebookConcreteBuilder()
    director = StoryDirector()
    director.construct(concrete_builder)
    director.basic_story()
    concrete_builder.story.show()

    concrete_builder2 = InstagramConcreteBuilder()
    director.construct(concrete_builder2)
    director.video_story()
    concrete_builder2.story.show()


# ==========================================
# Questions 1 & 2: Sandwich Builder
# ==========================================
class Sandwich:
    def __init__(self, name: str):
        self.name = name
        self.ingredients = []

    def add(self, ingredient: str):
        self.ingredients.append(ingredient)

    def show(self):
        print(f"{self.name}: {self.ingredients}")


class SandwichBuilder(ABC):
    def __init__(self, name: str):
        self.sandwich = Sandwich(name)

    @abstractmethod
    def build_base(self):
        pass

    @abstractmethod
    def build_filling(self):
        pass

    @abstractmethod
    def build_topping(self):
        pass


class ShawarmaSandwichBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__("Shawarma Sandwich")

    def build_base(self):
        self.sandwich.add("pita")

    def build_filling(self):
        self.sandwich.add("shawarma meat")

    def build_topping(self):
        self.sandwich.add("garlic sauce & fries")


class GroundMeatSandwichBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__("Ground Meat Sandwich")

    def build_base(self):
        self.sandwich.add("baguette")

    def build_filling(self):
        self.sandwich.add("ground meat")

    def build_topping(self):
        self.sandwich.add("cheese & herbs")


class FriedOmeletSandwichBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__("Fried with Omelet Sandwich")

    def build_base(self):
        self.sandwich.add("sandwich bread")

    def build_filling(self):
        self.sandwich.add("fried omelet")

    def build_topping(self):
        self.sandwich.add("ketchup & mayo")


class SandwichDirector:
    def __init__(self):
        self._builder = None

    def construct(self, builder: SandwichBuilder):
        self._builder = builder
        self._builder.build_base()
        self._builder.build_filling()
        self._builder.build_topping()
        return self._builder.sandwich


def run_sandwich_builder():
    print("\n=== Sandwich Builder ===")
    director = SandwichDirector()
    for builder in (
        ShawarmaSandwichBuilder(),
        GroundMeatSandwichBuilder(),
        FriedOmeletSandwichBuilder(),
    ):
        director.construct(builder).show()


# ==========================================
# Question 3: Car Builder by Order Options
# ==========================================
class Car:
    def __init__(self, model: str):
        self.model = model
        self.options = []

    def add_option(self, option: str):
        self.options.append(option)

    def show(self):
        print(f"{self.model} -> options: {self.options if self.options else ['base only']}")


class CarBuilder:
    def __init__(self, model: str = "Standard Car"):
        self.car = Car(model)

    def with_air_conditioning(self):
        self.car.add_option("Air Conditioning")
        return self

    def with_gps(self):
        self.car.add_option("GPS")
        return self

    def with_sunroof(self):
        self.car.add_option("Sunroof")
        return self

    def with_parking_camera(self):
        self.car.add_option("Parking Camera")
        return self

    def get_car(self) -> Car:
        return self.car


class CarOrderDirector:
    def build_basic(self) -> Car:
        return CarBuilder("Basic Car").get_car()

    def build_full(self) -> Car:
        return (
            CarBuilder("Full Option Car")
            .with_air_conditioning()
            .with_gps()
            .with_sunroof()
            .with_parking_camera()
            .get_car()
        )

    def build_custom(self, ac=False, gps=False, sunroof=False, camera=False) -> Car:
        builder = CarBuilder("Custom Order Car")
        if ac:
            builder.with_air_conditioning()
        if gps:
            builder.with_gps()
        if sunroof:
            builder.with_sunroof()
        if camera:
            builder.with_parking_camera()
        return builder.get_car()


def run_car_builder():
    print("\n=== Car Builder ===")
    director = CarOrderDirector()
    director.build_basic().show()
    director.build_full().show()
    director.build_custom(ac=True, camera=True).show()


if __name__ == "__main__":
    run_story_builder()
    run_sandwich_builder()
    run_car_builder()