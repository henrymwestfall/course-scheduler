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
    rawCourses = [("Pottery 1", CourseType.ELECTIVE)] # example course already in list
    rawStudentRequests = {} # map student name to requests (strings)
    rawStudentGrades = {} # map student name to the grade they're in
    rawTeacherQualifications = {} # map teacher name to qualifications (strings)
    rawTeacherRequestedOpenPeriods = {} # map teacher name to requested open periods


    # create Courses, Students, and Teachers
    courses = {} # maps course name to object
    for c in rawCourses:
        courses[c[0]] = Course(*c)

    students = []
    for studentName, requestList in rawStudentRequests.items():
        student = Student(studentName, rawStudentGrades[studentName])
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
    students, teachers = load_students_and_teachers()

    numGroups = 4

    # prepare data to feed to K-Means
    features = []
    for student in students:
        features.append(student.getReqVector())
    for teacher in teachers:
        features.append(teacher.getQualificationVector())

    # group students with K-Means clustering
    whitened = whiten(np.array(features))
    _, labels = kmeans2(whitened, numGroups)

    # group Student objects from K-Means result
    groups = [{"Students": [], "Teachers": []} for i in range(numGroups)]
    for i, indv in enumerate(students + teachers):
        if isinstance(indv, Student):
            groups[labels[i]]["Students"](indv)
        elif isinstance(indv, Teacher):
            groups[labels[i]]["Teachers"](indv)
    
    # solve each group
    all_existing_sections = []
    solutions = []
    for i, group in enumerate(groups):
        problem = LpProblem(f"Group{i}")
        add_constraints_from_individuals(problem, *group.values())
        define_global_constraints(problem)

        status = problem.solve()
        solutions.append(status)

        group_sections = create_final_sections(*groups.values())
        all_existing_sections = group_sections
    
    success = all([solution == "Optimal" for solution in solutions])
    print(f"Feasible: {success}")

if __name__ == "__main__":
    solve()