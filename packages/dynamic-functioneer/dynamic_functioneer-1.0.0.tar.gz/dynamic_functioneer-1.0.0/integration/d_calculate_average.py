def calculate_average(numbers):
    """
    Calculates the average of a list of numbers.

    Args:
        numbers (list of float): A list of numeric values.

    Returns:
        float: The average of the list.
    """
    # Handle empty list case to avoid division by zero
    if not numbers:
        return 0.0

    # Calculate the sum of all numbers
    total = sum(numbers)

    # Calculate the average by dividing the sum by the count
    average = total / len(numbers)

    return average