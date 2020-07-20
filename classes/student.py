from __future__ import annotations
from typing import TYPE_CHECKING, List
from pulp import LpVariable, LpAffineExpression, value
from .schedule import Schedule
from .course import CourseType, Section
from utils import summation
from .individual import Individual
if TYPE_CHECKING:
    from .course import Course
    
class Student(Individual):
    def __init__(self, tag: int, allCourses: List[str], grade: int):
        super().__init__(tag, allCourses)
        self.grade = grade
        self.reqAll = []

    def addSection(self, newSection: Section):
        """
        Adds a section
        """
        res = self.schedule.addSection(newSection)
        if res:
            self.addToSection(newSection)
    
    def removeSection(self, section: Section):
        """
        Removes a section. Does not require period number.
        """
        self.schedule.removeSection(section)

    def requestAll(self, newCourses: List[Course]):
        """
        Adds requested courses
        """

        for c in newCourses:
            if c not in self.reqAll:
                self.reqAll.append(c)
    
    def getGrade(self) -> int:
        """
        Get grade that student is going into.
        """
        return self.grade

    def getReqCore(self) -> List[Course]:
        """
        Get requested core Courses.
        """
        return [c for c in self.reqAll if c.courseType == CourseType.CORE]
    
    def getReqElectives(self) -> List[Course]:
        """
        Get requested elective Courses.
        """
        return [c for c in self.reqAll if c.courseType == CourseType.ELECTIVE]
    
    def getReqOff(self) -> List[Course]:
        """
        Get requested off periods (Courses).
        """
        return [c for c in self.reqAll if c.courseType == CourseType.OFF]
    
    def removeRequest(self, removed: Course):
        """
        Removes Course removed from reqAll.
        """
        if removed in self.reqAll:
            self.reqAll.remove(Course)

    def getReqVector(self, allCourseCodes: List[str]) -> List[int]:
        """
        Returns request vector from a list of all course codes.
        """

        ret = []
        codes = [x.courseCode for x in self.reqAll]
        for x in allCourseCodes:
            if x in codes:
                ret.append(1)
            else:
                ret.append(0)
        return ret
    """
    TODO: Fix or remove?
    def getReqCheck(self):
        Returns a generator checking if the requests all appear.
        
        currScheduleVals = list(self.schedule.getSections().values())
        for course in self.reqAll:
            yield (currScheduleVals.count(course) == self.reqAll.count(course))
    """
    def getConstraints(self):
        """
        Lazily generate all constraints by calling other constraint generator
        methods.
        """

        for c in super().getConstraints():
            yield c

        for c in self.getRequestCheckConstraints():
            yield c

    def getRequestCheckConstraints(self):
        """
        Lazily generate constraints checking if requested courses appear
        """

        for course in self.allCourses:
            isRequested = 0
            if course in self.reqAll:
                isRequested = 1

            varList = []
            for period in range(self.schedule.periods):
                variable = self.schedule.lpVars[period][int(course.courseCode)]
                varList.append(variable)
            sumOfVariables = summation(varList)

            yield sumOfVariables == isRequested

    def addToSection(self, section):
        section.addStudent(self)
    
    def getOpenScore(self) -> int:
        """
        Returns number of off periods requested that are there.
        """

        reqOff = [c.courseCode for c in self.getReqOff()]
        actualOff = [s.courseCode for s in self.schedule.getOffPeriods()]

        return len(list(set(reqOff) & set(actualOff)))

