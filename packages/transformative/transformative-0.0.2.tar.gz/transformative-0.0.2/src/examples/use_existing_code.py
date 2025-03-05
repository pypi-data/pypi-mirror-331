"""Example showing how to use autoconvert's convert and create functions"""

from generated_code.mock_autoconvert_funcs import SimpleInput, SimpleOutput

from src.conversion import init, convert, create


def main():
    # Initialize autoconvert with debug output
    init(debug_level=2)

    # Example data
    numbers = SimpleInput(numbers=[1, 2, 3, 4, 5])

    # Method 1: Using convert() - directly converts the data
    stats1 = convert(numbers, SimpleOutput, description="Converts a list of numbers into their sum and average")
    print(f"\nConvert result: {stats1}")

    # Method 2: Using create() - returns a reusable conversion function
    numbers_to_stats = create(SimpleInput, SimpleOutput, description="Converts a list of numbers into their sum and average")
    stats2 = numbers_to_stats(numbers)
    print(f"\nCreate result: {stats2}")


if __name__ == "__main__":
    main()
