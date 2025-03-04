def get_grade(self, student_name, course_name):
    """
    Retrieves the grade for a specific course.

    Args:
        student_name (str): The name of the student.
        course_name (str): The name of the course.

    Returns:
        float: The grade for the course.

    Raises:
        KeyError: If the student or course does not exist.

    Examples:
        >>> grades = StudentGrades()
        >>> grades.add_grade("Alice", "Math", 95.0)
        >>> grades.get_grade("Alice", "Math")
        95.0

        >>> grades.get_grade("Bob", "Math")
        Traceback (most recent call last):
            ...
        KeyError: "Student 'Bob' not found."

        >>> grades.get_grade("Alice", "Science")
        Traceback (most recent call last):
            ...
        KeyError: "Course 'Science' not found for student 'Alice'."
    """
    # Check if the student exists in the grades dictionary
    if student_name not in self.grades:
        raise KeyError(f"Student '{student_name}' not found.")

    # Check if the course exists for the given student
    if course_name not in self.grades[student_name]:
        raise KeyError(f"Course '{course_name}' not found for student '{student_name}'.")

    # Return the grade for the specified student and course
    return self.grades[student_name][course_name]