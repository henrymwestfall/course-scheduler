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
    __slots__ = ["_tag", "_schedule", "_reqOffPeriods", "_allCourses", "_grade", "_reqAll", "_altElectives"]
    def __init__(self, tag: int, allCourses: List[str]):
        super().__init__(tag, allCourses)
        self._grade = 0
        self._reqAll = []
        self._altElectives = []
    
    def addGrade(self, grade: int):
        self._grade = grade
    
    def addSection(self, newSection: Section):
        """
        Adds a section
        """
        res = self._schedule.addSection(newSection)
        if res:
            self.addToSection(newSection)
    
    def removeSection(self, section: Section):
        """
        Removes a section. Does not require period number.
        """
        self._schedule.removeSection(section)

    def requestAll(self, newCourses: List[Course]):
        """
        Adds requested courses
        """

        for c in newCourses:
            if c not in self._reqAll:
                self._reqAll.append(c)
    
    def getGrade(self) -> int:
        """
        Get grade that student is going into.
        """
        return self._grade

    def getReqCore(self) -> List[Course]:
        """
        Get requested core Courses.
        """
        return [c for c in self._reqAll if c._courseType == CourseType.CORE]
    
    def getReqElectives(self) -> List[Course]:
        """
        Get requested elective Courses.
        """
        return [c for c in self._reqAll if c._courseType == CourseType.ELECTIVE]
    
    def getReqOff(self) -> List[Course]:
        """
        Get requested off periods (Courses).
        """
        return [c for c in self._reqAll if c.courseType == CourseType.OFF]
    
    def removeRequest(self, removed: Course):
        """
        Removes Course removed from reqAll.
        """
        if removed in self._reqAll:
            self._reqAll.remove(Course)

    def getReqVector(self) -> List[int]:
        """
        Returns request vector from a list of all course codes.
        """

        ret = []
        codes = [req.courseCode for req in self._reqAll] # slower than set but less memory
        for course in self._allCourses:
            code = course._courseCode
            if code in codes:
                ret.append(1)
            else:
                ret.append(0)
        return ret

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

        for course in self._allCourses:
            isRequested = 0
            if course in self._reqAll:
                isRequested = 1

            varList = []
            for period in range(self._schedule.periods):
                variable = self._schedule._lpVars[period][int(course._courseCode)]
                varList.append(variable)
            sumOfVariables = summation(varList)

            yield sumOfVariables == isRequested

    def addToSection(self, section):
        section.addStudent(self)
        self._schedule.addSection(section)
    
    def getOpenScore(self) -> int:
        """
        Returns number of off periods requested that are there.
        """

        reqOff = [c.courseCode for c in self.getReqOff()]
        actualOff = [s.courseCode for s in self._schedule.getOffPeriods()]

        return len(list(set(reqOff) & set(actualOff)))

    def getElectiveCost(self) -> int:
        """
        Return an expression equal to the number of requested electives
        in schedule.
        """

        reqElective = [c._courseCode for c in self.getReqElectives()]
        for course in self._allCourses:
            if course._courseCode in reqElective:
                varList = [] # list of Lp variables at this elective and this period
                for period in range(self._schedule.periods):
                    variable = self._schedule._lpVars[period][int(course._courseCode)]
                    varList.append(variable)
                # add the sum of variables. This should be 0 or 1 because of other hard
                # constraints. 1 is good, and since the formula minimizes, the sum should 
                # be subtracted
                yield -summation(varList)

    def addAltElective(self, elective: Course):
        if not elective in self._altElectives:
            self._altElectives.append(elective)
    
    def removeAltElective(self, elective: Course):
        if elective in self._altElectives:
            self._altElectives.append(elective)
    