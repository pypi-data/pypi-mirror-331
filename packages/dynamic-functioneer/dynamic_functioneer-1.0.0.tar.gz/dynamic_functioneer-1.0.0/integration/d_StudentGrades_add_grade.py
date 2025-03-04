def add_grade(self, student_name, course_name, grade):
    """
    Adds or updates a student's grade for a specific course.

    Args:
        student_name (str): The name of the student.
        course_name (str): The name of the course.
        grade (float): The grade to assign to the student for the course.

    Returns:
        str: Confirmation message about the added or updated grade.

    Examples:
        >>> grades = StudentGrades()
        >>> grades.add_grade("Alice", "Math", 95.0)
        'Added grade for Alice in Math with grade 95.0'

        >>> grades.add_grade("Alice", "Math", 98.0)
        'Updated grade for Alice in Math to 98.0'

        >>> grades.grades
        {'Alice': {'Math': 98.0}}
    """
    # Check if the student already exists in our records
    if student_name in self.grades:
        # Check if the course already exists for this student
        if course_name in self.grades[student_name]:
            # Update existing grade
            self.grades[student_name][course_name] = grade
            return f"Updated grade for {student_name} in {course_name} to {grade}"
        else:
            # Add new course for existing student
            self.grades[student_name][course_name] = grade
    else:
        # Create new student entry with the course
        self.grades[student_name] = {course_name: grade}

    # Return confirmation message for new grade
    return f"Added grade for {student_name} in {course_name} with grade {grade}"