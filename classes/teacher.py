from __future__ import annotations
from typing import TYPE_CHECKING, List

from .individual import Individual
from utils import summation

if TYPE_CHECKING:
    from .course import Course, Section


class Teacher(Individual):
    def __init__(self, tag: int, allCourses: List[str], qualifications: List[str], openPeriods: list):
        super().__init__(tag, allCourses)
        self.qualifications = qualifications
        self.openPeriods = openPeriods
    
    def isQualified(self, courseCode: str) -> bool:
        """
        Returns whether a teacher is qualified for a particular courseCode.
        """
        
        return (courseCode in self.qualifications)
    
    def getOpenPeriods(self) -> List[int]:
        """
        Returns open periods numbers.
        """

        return self.openPeriods
    
    def isOpen(self, period: int) -> bool:
        """
        Returns whether a particular period is open.
        """

        return (period in self.openPeriods)

    def addSection(self, newSection: Section):
        """
        Adds a section to the schedule.
        """

        res = self.schedule.addSection(newSection)
        if res: self.openPeriods.remove(newSection.period)
    
    def removeSection(self, section: Section):
        """
        Removes a section from the schedule.
        """

        self.schedule.removeSection(section)
        self.openPeriods.append(section.period)
        self.openPeriods.sort()
    
    def getQualified(self):
        """
        Yields whether or not teacher is qualified for each class teaching.
        """

        currScheduleVals = list(self.schedule.getSections().values())
        for section in currScheduleVals:
            yield (section == None or self.isQualified(section.courseCode))
    
    def getQualificationVector(self) -> List[int]:
        """
        Returns (eager) of the teacher's qualifications
        """
        vector = [0] * len(self.allCourses)
        for course in self.qualifications:
            index = self.allCourses.index(course)
            vector[index] = 1

        return vector
    
    def getConstraints(self):
        """
        Lazily generate all constraints by calling other constraint generator
        methods.
        """

        for c in super().getConstraints():
            yield c

        for c in self.getQualifiedTeachingConstraints():
            yield c


    def getQualifiedTeachingConstraints(self):
        """
        Lazily generate constraints ensuring this teacher only teaches sections
        that they are qualified to teach.
        """

        for course in self.allCourses:
            isQualified = 0
            if course in self.qualifications:
                isQualified = 1
            
            varList = []
            for period in range(self.schedule.periods):
                variable = self.schedule.lpVars[period][int(course.courseCode)]
                varList.append(variable)
            sumOfVariables = summation(varList)

            yield sumOfVariables <= isQualified
    
    def addToSection(self, section):
        section.changeInstructor(self)
    
    def getOpenScore(self) -> int:
        """
        Returns number of off periods
        """
        return len(self.openPeriods)
