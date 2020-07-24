from __future__ import annotations
from typing import TYPE_CHECKING, List
from pulp import LpVariable, LpAffineExpression, value
from .schedule import Schedule
from .course import CourseType, Section
from utils import summation
if TYPE_CHECKING:
    from .course import Course

# Base class Individual and inheriting classes Student and Teacher for storing information for people.
class Individual:
    __slots__ = ["tag", "allCourses"]
    def __init__(self, tag: int, allCourses: List[Course]):
        self.tag = tag
        self.schedule = Schedule(tag, len(allCourses))
        self.reqOffPeriods = 1
        self.allCourses = allCourses
    
    def __str__(self):
        ret = "Individual with tag: " + str(self.tag)
        ret += "\n with schedule: " + str(self.schedule)
        return ret

    def changeReqOff(self, newReq: int):
        """
        Changes number of requested off periods.
        """
        self.reqOffPeriods = newReq
    
    def getReqOff(self) -> int:
        """
        Obtains number of requested off periods.
        """
        return self.reqOffPeriods
    
    def getSections(self):
        """
        Returns all the schedule along with empty periods.
        """
        return self.schedule.getSections()
    
    def getOffDelta(self):
        """
        Positive when more scheduled off than required, negative when fewer scheduled off than required
        """
        return (len(self.schedule.getOpenPeriods()) - self.reqOffPeriods)
    
    def hasPotentialLunchSlot(self, lunchPeriods: List[int]):
        """
        Return whether there is an open period in the potential lunch periods.
        """
        for period in self.schedule.getOpenPeriods():
            if period in lunchPeriods:
                return True
        return False

    def getConstraints(self):
        for c in self.getPeriodAttendanceConstraints():
            yield c

    def getPeriodAttendanceConstraints(self):
        """
        Lazily generate the constraints ensuring that only one section is
        assigned per period.
        """

        for courseVariables in self.schedule.lpVars:
            yield summation(courseVariables) <= 1

    def createSections(self) -> List[Section]:
        """
        Creates all necessary sections as if they do not exist yet.
        Currently this is eager. Consider making this lazy.
        """

        sections = []
        for period_list in self.schedule.lpVars:
            for variable in period_list:
                if value(variable) == 1:
                    # this course has been assigned at this period
                    tokens = self.schedule.parseVariableName(variable.name)
                    courseCode = tokens["course"]
                    new_section = Section(courseCode, CourseType.CORE) # TODO: put the correct course type
                    new_section.changePeriod(int(tokens["period"]) + 1) # add 1 to compensate for 0-based indexing

                    sections.append(new_section)
        
        return sections

    def addToSection(self, section):
        """
        Add this individual to the section. This should never be called on the Individual
        class because it is neither a Teacher nor a Student by default. Thus it must
        be overridden.
        """

        raise ValueError("Individual.addToSection must be overridden for valid call")
