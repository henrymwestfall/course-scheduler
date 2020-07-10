from pulp import LpProblem, LpAffineExpression, LpVariable, LpConstraint, LpStatus
from scipy.cluster.vq import vq, kmeans2, whiten
import numpy as np

from classes.individual import *
from classes.course import *
from classes.schedule import *
from utils import summation


def tag_generator():
    tag = 0
    while True:
        yield tag
        tag += 1

def load_students_and_teachers_and_courses():
    """
    Return a tuple containing a list of Teacher and Student objects.
    This loads the courses and adds them to the objects request/qualification
    lists.
    """

    # load the raw data
    # TODO: load from a file of some sort
    # student_requests = [
    #                 [0, 1, 3],
    #                 [0, 2, 3],
    #                 [0, 2, 4],
    #                 [1, 3, 4],
    #                 [0, 1, 2],
    #                 [1, 2, 3]
    # ]

    # teacher_qualifs = [
    #                 [0, 1, 3],
    #                 [0, 2, 4],
    #                 [1, 2, 3]
    # ]
    num_courses = 1
    student_requests = [
        [0]
    ]
    teacher_qualifs = [
        [0]
    ]

    rawCourses = [(str(i), CourseType.CORE) for i in range(num_courses)] # example course already in list
    rawStudentRequests = {i: reqs for i, reqs in enumerate(student_requests)} # map student name to requests (strings)
    rawStudentGrades = {i: 12 for i in range(len(student_requests))} # map student name to the grade they're in
    rawTeacherQualifications = {i: qualifs for i, qualifs in enumerate(teacher_qualifs)} # map teacher name to qualifications (strings)
    rawTeacherRequestedOpenPeriods = {i: 0 for i in range(len(teacher_qualifs))} # map teacher name to requested open periods

    # create tag generator
    tg = tag_generator()

    # create Courses, Students, and Teachers
    courses = {} # maps course name to object
    for c in rawCourses:
        courses[c[0]] = Course(*c)
    allCourses = list(courses.values())

    students = []
    for index, requestList in rawStudentRequests.items():
        student = Student(next(tg), rawStudentGrades[index], allCourses)
        students.append(student)
        student.requestAll([courses[str(c)] for c in requestList])

    teachers = []
    for index, qualifications in rawTeacherQualifications.items():
        qualifications_with_course_objects = [courses[str(q)] for q in qualifications]
        teacher = Teacher(next(tg), qualifications_with_course_objects, rawTeacherRequestedOpenPeriods[index], allCourses)
        teachers.append(teacher)

    return students, teachers, list(courses.values())
# Note: it would be nice if Teacher and Student constructors were more similar

def add_constraints_from_individual(problem, individual, individual_type_string):
    for constraint in individual.getConstraints():
        assertion_message = f"{individual_type_string} constraint was illegal"
        assert isinstance(constraint, LpConstraint), assertion_message
        problem += constraint

def add_constraints_from_individuals(problem, constraining_students, constraining_teachers, all_courses):
    """
    add constraints from constraining_students and constraining_teachers to problem.
    """

    for student in constraining_students:
        add_constraints_from_individual(problem, student, "student")
    for teacher in constraining_teachers:
        add_constraints_from_individual(problem, teacher, "teacher")

def define_sections_need_teachers_constraint(problem, students, teachers):
    """
    define the LpConstraint ensuring that each section assigned to a student
    has a qualified teacher assigned to it also.
    """

    all_constraints = []
    for student in students:
        for period, lpVars in student.schedule.lpVars.items():
            for class_id, attending in enumerate(lpVars):
                # get corresponding qualified teachers
                teacher_assignment_variables = []
                for teacher in teachers:
                    if teacher.getQualificationVector()[class_id] == 1:
                        teacher_assignment_variables.append(teacher.schedule.lpVars[period][class_id])
                c = summation(teacher_assignment_variables) >= attending
                all_constraints.append(c)
    return all_constraints

def define_global_constraints(problem, students, teachers):
    """
    add constraints that affect multiple individuals simultaneously to problem.
    """

    # set is ideal, but LpConstraints are unhashable
    all_constraints = []

    all_constraints += define_sections_need_teachers_constraint(problem, students, teachers)
    
    for c in all_constraints:
        assert isinstance(c, LpConstraint), "global constraint was illegal"
        problem += c

# create all sections locally in students
def create_final_sections(students, teachers):
    """
    return a list of the final Section objects with Students and Teachers added.
    """

    # build all sections
    allExistingSections = []

    for individual in students + teachers:
        new_sections = individual.createSections() # method not implemented yet
        for section in new_sections:
            for existingSection in allExistingSections:
                if section == existingSection:
                    break
            else:
                # the section doesn't exist yet, so add it to the existing sections
                individual.addToSection(section)
                allExistingSections.append(section)
                continue
            
            # the section already exists, so add the student/teacher there
            individual.addToSection(existingSection)
    
    return allExistingSections

def solve():
    """
    The main function
    """

    students, teachers, all_courses = load_students_and_teachers_and_courses()

    problem = LpProblem("Toy_Problem")
    add_constraints_from_individuals(problem, students, teachers, all_courses)
    define_global_constraints(problem, students, teachers)
    
    print(problem)
    status = problem.solve()
    all_existing_sections = create_final_sections(students, teachers)

    print(f"Solution is {LpStatus[status]}")
    for section in all_existing_sections:
        print(section)

if __name__ == "__main__":
    solve()
