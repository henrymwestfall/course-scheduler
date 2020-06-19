import unittest
from course import Course, CourseType, Section
from individual import Student, Teacher
from schedule import Schedule
from pulp import LpVariable, LpAffineExpression
from copy import deepcopy

class testIndividualMethods(unittest.TestCase):
    def setUp(self):
        self.stud = Student("test_s", 9, ["test_c_1"])
        self.teacher = Teacher("test_t", ["test"], [1, 2, 3, 4, 5, 6, 7, 8], ["test_c_1"])
        self.testCoreSection = Section("test", CourseType.CORE)
        self.testCoreSection.changePeriod(1)
        self.testCoreSection.changeInstructor(self.teacher)
        self.testCoreSection.addStudent(self.stud)
    
    def test_universal(self):
        right = {1: self.testCoreSection, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        blank = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        self.stud.addSection(self.testCoreSection)
        self.teacher.addSection(self.testCoreSection)
        self.assertEqual(self.stud.schedule.sections, right)
        self.assertEqual(self.teacher.schedule.sections, right)
        self.assertEqual(self.teacher.openPeriods, [2, 3, 4, 5, 6, 7, 8])
        
        self.stud.removeSection(self.testCoreSection)
        self.teacher.removeSection(self.testCoreSection)
        self.assertEqual(self.stud.schedule.sections, blank)
        self.assertEqual(self.teacher.schedule.sections, blank)
        self.assertEqual(self.teacher.openPeriods, [1, 2, 3, 4, 5, 6, 7, 8])

    def test_teacher(self):
        self.teacher.addSection(self.testCoreSection)
        for res in self.teacher.getQualified():
            self.assertTrue(res)
        
        right = [(LpVariable("test_t_1_0"), 1),
        (LpVariable("test_t_2_0"), 1),
        (LpVariable("test_t_3_0"), 1),
        (LpVariable("test_t_4_0"), 1),
        (LpVariable("test_t_5_0"), 1),
        (LpVariable("test_t_6_0"), 1),
        (LpVariable("test_t_7_0"), 1),
        (LpVariable("test_t_8_0"),1)]
        for res in self.teacher.getConstraints(["test"]):
            self.assertEqual(res, LpAffineExpression(right) <=1)

    def test_student(self):
        # remove, request vector, request checking, course checking
        testCore = Course("test_core", CourseType.CORE)
        testElective = Course("test_elective", CourseType.ELECTIVE)
        testOff = Course("test_off",CourseType.OFF)
        
        self.stud.addReqCore(testCore)
        self.assertEqual(self.stud.reqCores, [testCore])
        self.assertEqual(self.stud.reqAll, [testCore])
        
        self.stud.addReqElective(testElective)
        self.assertEqual(self.stud.reqElectives, [testElective])
        self.assertEqual(self.stud.reqAll, [testCore, testElective])
        
        self.stud.addReqOffPeriod(testOff)
        self.assertEqual(self.stud.reqOffPeriods, [testOff])
        self.assertEqual(self.stud.reqAll, [testCore, testElective, testOff])
        
        res1 = self.stud.getReqVector(["test_core", "test_elective", "test_off"])
        self.assertEqual(res1, [1, 1, 1])
        res2 = self.stud.getReqVector(["test_core", "test_elective", "test_offS"])
        self.assertEqual(res2, [1, 1, 0])
        
        right = [(LpVariable("test_s_1_0"), 1),
        (LpVariable("test_s_2_0"), 1),
        (LpVariable("test_s_3_0"), 1),
        (LpVariable("test_s_4_0"), 1),
        (LpVariable("test_s_5_0"), 1),
        (LpVariable("test_s_6_0"), 1),
        (LpVariable("test_s_7_0"), 1),
        (LpVariable("test_s_8_0"),1)]
        
        
        for res in self.stud.getConstraints(["test"]):
            self.assertEqual(res, LpAffineExpression(right) == 1)
                

        self.stud.removeReqOff(testOff)
        self.assertEqual(self.stud.reqOffPeriods, [])
        self.assertEqual(self.stud.reqAll, [testCore, testElective])

        self.stud.removeReqElective(testElective)
        self.assertEqual(self.stud.reqElectives, [])
        self.assertEqual(self.stud.reqAll, [testCore])

        self.stud.removeReqCore(testCore)
        self.assertEqual(self.stud.reqCores, [])
        self.assertEqual(self.stud.reqAll,[])

if __name__ == "__main__":
    unittest.main()