from math import pi


def welcome():
    print("Hello, welcome to my package!")


def circle_area(radius: float) -> float:
    """Compute the area of a circle."""
    return pi * (radius**2)
