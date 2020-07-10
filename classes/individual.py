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
    
    def addSection(self, newSection: Section):
        """
        Adds a section
        """
        x = self.schedule.addSection(newSection)
    
    def removeSection(self, section: Section):
        """
        Removes a section. Does not require period number.
        """
        self.schedule.removeSection(section)
    
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

        for courseVariables in self.schedule.lpVars.values():
            yield summation(courseVariables) <= 1

    def createSections(self) -> List[Section]:
        """
        Creates all necessary sections as if they do not exist yet.
        Currently this is eager. Consider making this lazy.
        """

        sections = []
        for period_list in self.schedule.lpVars.values():
            for variable in period_list:
                if value(variable) == 1:
                    # this course has been assigned at this period
                    tokens = self.schedule.parseVariableName(variable.name)
                    courseCode = tokens["course"]
                    new_section = Section(courseCode, CourseType.CORE) # TODO: put the correct course type
                    new_section.changePeriod(int(tokens["period"]))

                    sections.append(new_section)
        
        return sections

    def addToSection(self, section):
        """
        Add this individual to the section. This should never be called on the Individual
        class because it is neither a Teacher nor a Student by default. Thus it must
        be overridden.
        """

        raise ValueError("Individual.addToSection must be overridden for valid call")

        
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
            for period in self.schedule.lpVars.keys():
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

class Student(Individual):
    def __init__(self, tag: int, allCourses: List[str], grade: int):
        super().__init__(tag, allCourses)
        self.grade = grade
        self.reqAll = []

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
            for period in self.schedule.lpVars.keys():
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

