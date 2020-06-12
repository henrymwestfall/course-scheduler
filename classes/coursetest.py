import unittest
from course import Course, CourseType, Section
from individual import Student, Teacher
from schedule import Schedule
class TestCourseMethods(unittest.TestCase):
    def setUp(self):
        self.course = Course("test", CourseType.CORE)
        self.otherCourse = Course("test2", CourseType.CORE)
        self.testTeach = Teacher("test_t", ["test"], [1],[])
        self.testStudent = Student("test_s", 9,[])
    
    def test_eq(self):
        self.assertNotEqual(self.course, self.otherCourse)
        self.otherCourse.courseCode = "test"
        self.assertEqual(self.course, self.otherCourse)
    
    def test_add_del(self):
        self.course.addReqStudent()
        self.assertEqual(self.course.getReqStudents(), 1)
        
        self.course.addTeacher(self.testTeach)
        self.assertEqual(self.course.getTeachers(), [self.testTeach])
        self.assertEqual(self.course.potentialPeriods, [1])

        self.course.removeReqStudent()
        self.assertEqual(self.course.getReqStudents(), 0)

        
        self.course.removeTeacher(self.testTeach)
        self.assertEqual(self.course.getTeachers(), [])
        self.assertEqual(self.course.potentialPeriods, [])
    
    def test_section(self):
        self.section = self.course.newSection()
        self.otherCourse.addTeacher(self.testTeach)
        self.otherCourse.courseCode = "test"
        self.otherSection = self.otherCourse.newSection()

        self.assertTrue(self.section.sameBaseCourse(self.otherSection))
        self.otherSection.courseCode = "test2"
        self.assertFalse(self.section.sameBaseCourse(self.otherSection))
        self.otherSection.courseCode = "test"

        self.section.changePeriod(1)
        self.otherSection.changePeriod(1)
        self.assertEqual(self.section.getPeriod(), 1)
        
        self.section.changeInstructor(self.testTeach)
        self.otherSection.changeInstructor(self.testTeach)
        self.assertEqual(self.section.getInstructor(),self.testTeach)
        
        self.section.addStudent(self.testStudent)
        self.otherSection.addStudent(self.testStudent)
        self.assertEqual(self.section.getStudents(), [self.testStudent])
        self.assertEqual(self.section.getStudentCount(), 1)
        self.assertTrue(self.section.isTaking(self.testStudent))
        
        self.assertTrue(self.section.isValid())
        self.assertEqual(self.section, self.otherSection)
        
        self.assertEqual(str(self.section),"CourseCode: test\n of type: CORE\n with teacher: test_t\n in period: 1\n with students: [\'test_s\']")

        self.assertTrue(self.section.isValid())
        self.assertEqual(self.section, self.otherSection)

        self.section.removeStudent(self.testStudent)
        self.assertEqual(self.section.getStudents(),[])

    
if __name__ == "__main__":
    unittest.main()