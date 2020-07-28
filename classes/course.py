from __future__ import annotations
from typing import TYPE_CHECKING, List
from enum import Enum
from utils import summation
if TYPE_CHECKING:
    from .individual import Individual
    from .student import Student
    from .teacher import Teacher
    from .schedule import Schedule


# Defines classes relating to courses and sections.
# Courses represent an unscheduled verion of a generic class containing information regarding how it might be structured
# Section represents a scheduled version of a generic class containing information about the specific scheduled instance.

class CourseType(Enum):
    CORE = 0
    ELECTIVE = 1
    OFF = 2

class Course:
    __slots__ = ["_courseCode", "_qualifiedTeachers", "_potentialPeriods", "_reqTotalStudents","_courseType"]
    def __init__(self, courseCode: str, courseType: CourseType):
        self._courseCode = courseCode
        self._qualifiedTeachers = []
        self._potentialPeriods = []
        self._reqTotalStudents = 0
        self._courseType = courseType


    def __eq__(self, other) -> bool:
        """
        Tests whether Course is equivalent to other Course.

        __eq__ allows for use within ==, remove from list, etc.
        
        The Python "is" statement overrides this. 
        """
        if isinstance(other, Course):
            return self._courseCode == other._courseCode
        return False
    
    def addReqStudent(self):
        """
        Adds 1 student to number who want to take the class.
        """
        self._reqTotalStudents += 1
    
    def addTeacher(self, teacher: Teacher): 
        """
        Adds a teacher object to the list of qualified teachers and updates list of potential periods
        """
        if teacher.isQualified(self._courseCode):
            self._qualifiedTeachers.append(teacher)
            for period in teacher.openPeriods:
                if period not in self._potentialPeriods:
                    self._potentialPeriods.append(period)
    
    def getCourseCode(self) -> str:
        """
        Get course code.
        """
        return self._courseCode
    
    def getTeachers(self) -> List[Teacher]:
        """
        Get teachers qualified to teach class.
        """
        return self._qualifiedTeachers
    
    def getpotentialPeriods(self) -> List[int]:
        """
        Get potential periods for class to occur.
        """
        return self._potentialPeriods
    
    def getReqStudents(self) -> int:
        """
        Get number of students interested in the class.
        """
        return self._reqTotalStudents
    
    def getCourseType(self) -> CourseType:
        """
        Get the course type.
        """
        return self._courseType

    def newSection(self) -> Section:
        """
        Create a new section of a class.
        """
        return Section(self._courseCode, self._courseType)
    
    def removeTeacher(self, teacher: Teacher):
        """
        Remove a teacher from the list of qualified teachers, reevaluate periods.
        """
        self._qualifiedTeachers.remove(teacher)
        self._potentialPeriods = []
        for teacher in self._qualifiedTeachers:
            for period in teacher.openPeriods:
                if period not in self._potentialPeriods:
                    self._potentialPeriods.append(period)
    
    def removeReqStudent(self):
        """
        Remove 1 interested student.
        """
        self._reqTotalStudents -= 1
    
    def getGlobalConstr(self):
        ret = []
        for teacher in self._qualifiedTeachers:
            classindex = teacher.allCourses.index(self._courseCode)
            for p in range(1, 9):
                ret.append(teacher.schedule.lpVars[p][classindex])
        if self._reqTotalStudents > 0:
            attending = 1
        else:
            attending = 0
        return summation(ret) >= attending



class Section:
    __slots__ = ["_courseCode", "_courseType", "_instructor", "_period", "_students"]
    def __init__(self, courseCode: str, courseType: CourseType):
        self._courseCode = courseCode
        self._courseType = courseType
        self._instructor = None
        self._period = -1
        self._students = []

    def __str__(self) -> str:
        """
        Return string representation of Section
        """
        ret = f"CourseCode: {self._courseCode}"
        ret += f"\n\tof type: {self._courseType.name}"
        ret += f"\n\twith teacher: {self._instructor._tag}"
        ret += f"\n\tin period: {self._period}"
        ret += f"\n\twith students: {[stu._tag for stu in self._students]}"
        return ret

    def __eq__(self, other) -> bool:
        """
        Returns whether a Section is the same as another, excluding students.
        """
        if isinstance(other, Section):
            codeCorrect = (self._courseCode == other._courseCode)
            instructorCorrect = (self._instructor == other._instructor)
            courseTypeCorrect = (self._courseType == other._courseType)
            periodCorrect = (self._period == other._period)
            return (codeCorrect and instructorCorrect and courseTypeCorrect and periodCorrect)
        return False

    def sameBaseCourse(self, other: Section):
        """
        Returns whether the course code is the same as another Section.
        """
        return self._courseCode == other.courseCode

    def changeInstructor(self, teacher: Teacher):
        """
        Changes or adds (depending on whether instructor is None currently) the instructor.
        """
        self._instructor = teacher

    def changePeriod(self, period: int):
        """
        Changes or adds (depending on whether period is -1 currently) the period.
        """ 
        self._period = period
    
    def addStudent(self, student: Student):
        """
        Adds a student to the list.
        """
        if not self.isTaking(student):
            self._students.append(student)

    def getCourseCode(self) -> str:
        """
        Gets course code
        """
        return self._courseCode
    
    def getCourseType(self) -> CourseType:
        """
        Gets course type
        """
        return self._courseType

    def getInstructor(self) -> Teacher:
        """
        Gets instructor
        """
        return self._instructor
    
    def getPeriod(self) -> int:
        """
        Gets period
        """
        return self._period
    
    def getStudents(self) -> List[Student]:
        """
        Gets all students currently scheduled for Section.
        """
        return self._students
    
    def getStudentCount(self) -> int:
        """
        Gets total number of participating students.
        """
        return len(self._students)
    
    def isTaking(self, student: Student) -> bool:
        """
        Returns whether a student is taking the class.
        """
        return (student in self._students)
    
    def removeStudent(self, student: Student):
        """
        Removes a student from the class.
        """
        if self.isTaking(student):
            self._students.remove(student)
    
    def isValid(self):
        """
        Returns whether the Section is at least "valid" (all data types populated)
        """
        instructorValid = (self._instructor != None) and (self._instructor.isQualified(self._courseCode))
        # TODO: Add checks to make sure that two classes aren't at the same time?
        # TODO: If the Teacher instance makes changes to the root Teacher instance, it's easy.
        periodValid = (self._period != -1)
        studentsValid = (len(self._students) > 0)
        return (instructorValid and periodValid and studentsValid)
