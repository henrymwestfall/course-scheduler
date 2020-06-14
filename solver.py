from pulp import LpProblem, LpAffineExpression, LpVariable
from scipy.cluster.vq import vq, kmeans2, whiten
import numpy as np

from classes.individual import *
from classes.course import *
from classes.schedule import *


# define summation function (built-in sum does not work on Affine Expressions)
def summation(terms):
    """
    return a usable sum of `terms` where coefficients are 1
    """
    total = LpAffineExpression({t: 1 for t in terms})
    return total

def summation_test():
    """
    test the summation function and return a boolean of it's result.
    """

    test_1 = LpVariable("Test_1", lowBound = 0, upBound = 1, cat="Integer")
    test_2 = LpVariable("Test_2", lowBound = 0, upBound = 1, cat="Integer")
    test_3 = LpVariable("Test_3", lowBound = 0, upBound = 1, cat="Integer")
    if str(summation([test_1, test_2, test_3])) == "Test_1 + Test_2 + Test_3":
        print("Summation test passed.")
        return True
    else:
        print("Summation test failed.")
        return False

def load_students_and_teachers():
    """
    Return a tuple containing a list of Teacher and Student objects.
    This loads the courses and adds them to the objects request/qualification
    lists.
    """

    # load the raw data
    # TODO: load from a file of some sort
    student_requests = [
                    [0, 1, 3],
                    [0, 2, 3],
                    [0, 2, 4],
                    [1, 3, 4],
                    [0, 1, 2],
                    [1, 2, 3]
    ]

    teacher_qualifs = [
                    [0, 1, 3],
                    [0, 2, 4],
                    [1, 2, 3]
    ]

    rawCourses = [(str(i), CourseType.CORE) for i in range(5)] # example course already in list
    rawStudentRequests = {i: reqs for i, reqs in enumerate(student_requests)} # map student name to requests (strings)
    rawStudentGrades = {i: 12 for i in range(len(student_requests))} # map student name to the grade they're in
    rawTeacherQualifications = {i: qualifs for i, qualifs in enumerate(teacher_qualifs)} # map teacher name to qualifications (strings)
    rawTeacherRequestedOpenPeriods = {i: 0 for i in range(len(teacher_qualifs))} # map teacher name to requested open periods


    # create Courses, Students, and Teachers
    courses = {} # maps course name to object
    for c in rawCourses:
        courses[c[0]] = Course(*c)

    students = []
    for studentName, requestList in rawStudentRequests.items():
        student = Student(studentName, rawStudentGrades[studentName], rawCourses)
        students.append(student)
        student.requestAll([courses[c] for c in requestList]) # method not implemented (yet?)

    teachers = []
    for teacherName, qualifications in rawTeacherQualifications.items():
        teacher = Teacher(teacherName, qualifications, rawTeacherRequestedOpenPeriods[teacherName])
        teachers.append(teacher)

    return students, teachers
# Note: it would be nice if Teacher and Student constructors were more similar

def add_constraints_from_individuals(problem, constraining_students, constraining_teachers):
    """
    add constraints from constraining_students and constraining_teachers to problem.
    """

    for student in constraining_students:
        for constraint in student.getConstraints(): # method not implemented yet
            problem += constraint
    for teacher in constraining_teachers:
        for constraint in teacher.getConstraints(): # method not implemented yet
            problem += constraint

def define_global_constraints(problem):
    """
    add constraints that affect multiple individuals simultaneously to problem.
    """

    # TODO: define the constraint(s) that each class must have a teacher
    pass

# create all sections locally in students
def create_final_sections(students, teachers):
    """
    return a list of the final Section objects with Students and Teachers added.
    """

    # build all sections
    allExistingSections = []

    for individual in students + teachers:
        individual.schedule.createSections() # method not implemented yet
        for section in individual.schedule.sections:
            for existingSection in allExistingSections:
                if section == existingSection:
                    break
            else:
                # the section doesn't exist yet, so add it to the existing sections
                allExistingSections.append(section)
                continue
            
            # the section already exists, so add the student/teacher there
            if isinstance(individual, Teacher):
                existingSection.setTeacher(individual) # method not implemented yet
            else:
                existingSection.addStudent(individual)
    
    return allExistingSections

def solve():
    """
    The main function
    """

    students, teachers = load_students_and_teachers()

    problem = LpProblem("Toy Problem")
    add_constraints_from_individuals(problem, students, teachers)
    define_global_constraints(problem)

    status = problem.solve()
    all_existing_sections = create_final_sections(students, teachers)

    print(f"Solution is {status}")
    for section in all_existing_sections:
        print(section)

if __name__ == "__main__":
    solve()