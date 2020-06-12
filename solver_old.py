from pulp import LpProblem, LpAffineExpression, LpVariable

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
    test_1 = LpVariable("Test_1", lowBound = 0, upBound = 1, cat="Integer")
    test_2 = LpVariable("Test_2", lowBound = 0, upBound = 1, cat="Integer")
    test_3 = LpVariable("Test_3", lowBound = 0, upBound = 1, cat="Integer")
    if str(summation([test_1, test_2, test_3])) == "Test_1 + Test_2 + Test_3":
        print("Summation test passed.")
    else:
        print("Summation test failed.")


problem = LpProblem("Scheduler")


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

# Note: it would be nice if Teacher and Student constructors were similar


# get and add constraints from Students and Teachers
for student in students:
    for constraint in student.getConstraints(): # method not implemented yet
        problem += constraint
for teacher in teachers:
    for constraint in teacher.getConstraints(): # method not implemented yet
        problem += constraint


# TODO: define the constraint(s) that each class must have a teacher



# solve problem
status = problem.solve()
print(f"Solution is {status}")


# build all sections
allExistingSections = []

# create all sections locally in students
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