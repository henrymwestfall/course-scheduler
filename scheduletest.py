import unittest
from classes.course import Course, CourseType, Section
from classes.individual import Student, Teacher
from classes.schedule import Schedule
from pulp import LpVariable, LpAffineExpression
from copy import deepcopy
class TestCourseMethods(unittest.TestCase):
    def setUp(self):
        self.course = Course("test", CourseType.CORE)
        self.testTeach = Teacher("test_t", ["test"], [1], [])
        self.testStudent = Student("test_s", 9, [])
        self.section = self.course.newSection()
        self.section.changePeriod(1)
        self.section.changeInstructor(self.testTeach)
        self.section.addStudent(self.testStudent)
    
        self.schedule = Schedule("test_sched", 2)
    
    def testAll(self):
        self.assertEqual(self.schedule.getOpenPeriods(), [1, 2, 3, 4, 5, 6, 7, 8])
        self.schedule.addSection(self.section)
        self.assertEqual(self.schedule.getOpenPeriods(), [2, 3, 4, 5, 6, 7, 8])
        
        haveTeachers = [res for res in self.schedule.haveTeachers()]
        self.assertTrue(haveTeachers[0])

        expr1 = [constr for constr in self.schedule.getValidityConstr()]
        expr2 = LpAffineExpression([(LpVariable("test_sched_1_0"),1), (LpVariable("test_sched_1_1"),1)]) <= 1
        self.assertEqual(expr1[0], expr2)

        self.schedule.removeSection(self.section)
        self.assertEqual(self.schedule.getOpenPeriods(), [1, 2, 3, 4, 5, 6, 7, 8])
        
        
if __name__ == "__main__":
    unittest.main()