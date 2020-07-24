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
    __slots__ = ["tag", "allCourses", "grade"]
    def __init__(self, tag: int, allCourses: List[str], grade: int):
        super().__init__(tag, allCourses)
        self.grade = grade
        self.reqAll = []
        self.altElectives = []

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
    
    def getConstraints(self, allCourses: List[str]):
        """
        Yields constraints checking if each of the requested courses appear.
        """

        for course in allCourses:
            isRequested = 0
            if course in self.reqAll: 
                isRequested = 1
            
            ret = []
            for period in self.schedule.lpVars.keys():
                variable = self.schedule.lpVars[period][int(course.courseCode)]
                assert isinstance(variable, LpVariable)
                ret.append(variable)
            sum_of_ret = summation(ret)
            assert isinstance(sum_of_ret, LpAffineExpression)
            assert isinstance(sum_of_ret == isRequested, LpAffineExpression)

            yield sum_of_ret == isRequested

    def addToSection(self, section):
        section.addStudent(self)
    
    def getOpenScore(self) -> int:
        """
        Returns number of off periods requested that are there.
        """

        reqOff = [c.courseCode for c in self.getReqOff()]
        actualOff = [s.courseCode for s in self.schedule.getOffPeriods()]

        return len(list(set(reqOff) & set(actualOff)))
        # The above is a handy way of getting the combined information of two lists

    def getElectiveScore(self) -> int:
        reqElective = [c.courseCode for c in self.getReqElectives()]
        actualScore = 0
        for s in self.schedule.sections.keys():
            if s.courseType == CourseType.ELECTIVE:
                if s in self.getReqElectives():
                    actualScore += 5
                elif s in self.altElectives:
                    actualScore += 1
        return actualScore

    def addAltElective(self, elective: Course):
        if not elective in self.altElectives:
            self.altElectives.append(elective)
    
    def removeAltElective(self, elective: Course):
        if elective in self.altElectives:
            self.altElectives.append(elective)
    