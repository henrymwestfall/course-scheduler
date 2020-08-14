from pulp import LpProblem, LpAffineExpression, LpVariable, LpConstraint, LpStatus
from scipy.cluster.vq import vq, kmeans2, whiten
import numpy as np

from classes.student import Student
from classes.teacher import Teacher
from classes.course import *
from classes.schedule import *
from utils import summation
from problem_generator import ToyProblem

import matplotlib.pyplot as plt
def tag_generator():
    tag = 0
    while True:
        yield tag
        tag += 1


class Problem:
    def __init__(self):
        ret = self.load_toy_problem()#self.load_students_and_teachers_and_courses()
        self.students, self.teachers, self.courses = ret
        self.problem = LpProblem("Toy_Problem")

        self.existing_sections = []

    @property
    def status(self):
        return self.problem.status

    def add_constraints(self):
        self.add_constraints_from_individuals()
        self.define_global_constraints()

    def solve(self):
        self.add_constraints()
        self.problem.solve()
        self.create_final_sections()

    def display_result(self):
        print(f"Solution is {LpStatus[self.status]}")
        for section in self.existing_sections:
            print(section)
        print(self.students[0]._schedule)

    def load_students_and_teachers_and_courses(self):
        """
        Return a tuple containing a list of Teacher and Student objects.
        This loads the courses and adds them to the objects request/qualification
        lists.
        """

        # load the raw data
        # TODO: load from a file of some sort
        num_courses = 5
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
            student = Student(next(tg), allCourses)
            # set student grade to rawStudentGrades[index]
            students.append(student)
            student.requestAll([courses[str(c)] for c in requestList])

        teachers = []
        for index, qualifications in rawTeacherQualifications.items():
            qualifications_with_course_objects = [courses[str(q)] for q in qualifications]
            teacher = Teacher(next(tg), allCourses)
            teacher.addQualifications(qualifications_with_course_objects)
            # TODO: add open period requests from rawTeacherRequestedOpenPeriods[index]
            teachers.append(teacher)

        return students, teachers, list(courses.values())

    def load_toy_problem(self):
        p = ToyProblem(num_teachers=24, num_students=200, num_courses=20, num_periods=8, num_pathways=2)
        return p.students, p.teachers, p.all_courses

    def add_constraints_from_individuals(self):
        """
        Add constraints from constraining_students and constraining_teachers to problem.
        """

        for student in self.students:
            self.add_constraints_from_individual(student, "student")
        for teacher in self.teachers:
            self.add_constraints_from_individual(teacher, "teacher")
    
    def add_constraints_from_individual(self, individual, individual_type_string):
        for constraint in individual.getConstraints():
            assertion_message = f"{individual_type_string} constraint was illegal"
            assert isinstance(constraint, LpConstraint), assertion_message
            self.problem += constraint

    def get_sections_need_teachers_constraints(self):
        """
        Define the LpConstraint ensuring that each section assigned to a student
        has a qualified teacher assigned to it also.
        """

        all_constraints = []
        for student in self.students:
            for period, lpVars in enumerate(student._schedule._lpVars):
                for class_id, attending in enumerate(lpVars):
                    # get corresponding qualified teachers
                    teacher_assignment_variables = []
                    for teacher in self.teachers:
                        if teacher.getQualificationVector()[class_id] == 1:
                            teacher_assignment_variables.append(teacher._schedule._lpVars[period][class_id])
                    c = summation(teacher_assignment_variables) >= attending
                    all_constraints.append(c)
        """
        Using getGlobalConstr:

        allConstrs = []
        for course in self.courses:
            allConstrs.append(course.getGlobalConstr())
        return allConstrs
        """
        return all_constraints

    def define_global_constraints(self):
        """
        Add constraints that affect multiple individuals simultaneously to problem.
        """

        # set is ideal, but LpConstraints are unhashable
        all_constraints = []

        all_constraints += self.get_sections_need_teachers_constraints()
        
        for c in all_constraints:
            assert isinstance(c, LpConstraint), "global constraint was illegal"
            self.problem += c

    def create_final_sections(self):
        """
        Return a list of the final Section objects with Students and Teachers added.
        """

        # build all sections
        for individual in self.students + self.teachers:
            new_sections = individual.createSections() # method not implemented yet
            for section in new_sections:
                for existing_section in self.existing_sections:
                    if section == existing_section:
                        break
                else:
                    # the section doesn't exist yet, so add it to the existing sections
                    individual.addToSection(section)
                    self.existing_sections.append(section)
                    continue
                
                # the section already exists, so add the student/teacher there
                individual.addToSection(existing_section)

    def sectionSizeHist(self):
        """
        Returns data for creating a histogram for section size

        Returns: Dictionary of class size to frequency.
        """
        
        ret = {}
        for sect in self.existing_sections:
            if len(sect._students) in ret.keys():
                ret[len(sect._students)] += 1
            else:
                ret[len(sect._students)] = 1

        sectSizeFig, sectSizeAx = plt.subplots()
        sectSizeAx.bar(ret.keys(), ret.values())
        
        sectSizeAx.set_xlabel("Class size")
        sectSizeAx.set_ylabel("Frequency")
        sectSizeAx.set_title("Class Size Distribution")
        plt.show()
        

if __name__ == "__main__":
    #solve()
    p = Problem()
    p.solve()
    p.display_result()
    p.sectionSizeHist()