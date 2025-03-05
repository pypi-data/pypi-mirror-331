"""Example showing how to generate new conversion functions with autoconvert"""

from dataclasses import dataclass

from src.conversion import init, convert, create


@dataclass
class Circle:
    """A circle defined by its radius"""

    radius: float


@dataclass
class Square:
    """A square defined by its side length"""

    side: float


def main():
    # Initialize autoconvert with debug output
    init(debug_level=2)
    clobber_existing_files = True

    # Expected: Square with side = sqrt(pi * radius^2)
    # For radius=5: side ≈ 8.86

    # Try to convert Circle to Square with equal area
    # Method 1: Direct conversion
    square1 = convert(Circle(radius=5.0), Square, description="Convert a circle to a square with the same area", debug_level=5, clobber_existing_files=clobber_existing_files)
    print(f"\nConvert result: {square1}")

    # Method 2: Get reusable conversion function
    circle_to_square = create(Circle, Square, description="Convert a circle to a square with the same area", debug_level=5, clobber_existing_files=False)
    square2 = circle_to_square(Circle(radius=5.0))
    print(f"\nCreate result: {square2}")


if __name__ == "__main__":
    main()
