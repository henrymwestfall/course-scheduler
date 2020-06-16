from __future__ import annotations
from typing import TYPE_CHECKING, List
from pulp import LpVariable, LpAffineExpression
from .schedule import Schedule
from .course import CourseType
from utils import summation
if TYPE_CHECKING:
    from .course import Course, Section

# Base class Individual and inheriting classes Student and Teacher for storing information for people.
class Individual:
    def __init__(self, tag: int, allCourses: list):
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
    
    def hasPotentialLunchSlot(self, lunchPeriods: list):
        """
        Return whether there is an open period in the potential lunch periods.
        """
        for period in self.schedule.getOpenPeriods():
            if period in lunchPeriods:
                return True
        return False
    
        
class Teacher(Individual):
    def __init__(self, tag: int, qualifications: list, openPeriods: list, allCourses: list):
        super().__init__(tag, allCourses)
        self.qualifications = qualifications
        self.openPeriods = openPeriods
    
    def isQualified(self, courseCode: str) -> bool:
        """
        Returns whether a teacher is qualified for a particular courseCode.
        """
        return (courseCode in self.qualifications)
    
    def getOpenPeriods(self) -> list:
        """
        Returns open periods.
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
    
    def getQualified(self):
        """
        Yields whether or not teacher is qualified for each class teaching.
        """
        currScheduleVals = list(self.schedule.getSections().values())
        for section in self.currScheduleVals:
            yield (self.isQualified(section.courseCode))

    def getQualificationVector(self):
        """
        Returns (eager) of the teacher's qualifications
        """
        vector = [0] * len(self.allCourses)
        for course in self.qualifications:
            index = self.allCourses.index(course)
            vector[index] = 1

        return vector
        #raise NotImplementedError("Method not yet implemented")
    
    def getConstraints(self, allCourses: list):
        """
        Yields constraints determining whether a teacher is qualified for a specific course.
        """
        index = 0
        for courseCode in allCourses:
            isQualified = 0
            if courseCode in self.qualifications: isQualified = 1
            
            ret = []
            for period in self.schedule.lpVars.keys():
                ret.append(self.schedule.lpVars[period][index])
            
            yield (summation(ret) <= isQualified)

class Student(Individual):
    def __init__(self, tag: int, grade: int, allCourses: list):
        super().__init__(tag, allCourses)
        self.grade = grade
        self.reqCores = []
        self.reqElectives = []
        self.reqOffPeriods = []
        self.updateReqAll()
    
    def updateReqAll(self):
        """
        Adds to list of all requested classes.
        """
        self.reqAll = self.reqCores
        self.reqAll.extend(self.reqElectives)
        self.reqAll.extend(self.reqOffPeriods)

    def addReqCore(self, newCore: Course):
        """
        Adds a requested core class.
        """
        if newCore not in self.reqCores:
            self.reqCores.append(newCore)
            self.reqAll.append(newCore)

    def addReqElective(self, newElective: Course):
        """
        Adds a requested elective class.
        """
        if newElective not in self.reqElectives:
            self.reqElectives.append(newElective)
            self.reqAll.append(newElective)

    def requestAll(self, newCourses: List[Course]):
        """
        Adds requested courses
        """

        for c in newCourses:
            if c.courseType == CourseType.CORE:
                self.addReqCore(c)
            elif c.courseType == CourseType.ELECTIVE:
                self.addReqElective(c)
    
    def addReqOffPeriod(self, newOff: Course):
        """
        Adds a requested off period. Off period must be a course.
        """
        if newOff not in self.reqOffPeriods:
            self.reqOffPeriods.append(newOff)
            self.reqAll.append(newOff)
    
    def getGrade(self) -> int:
        """
        Get grade that student is going into.
        """
        return self.grade

    def getReqCore(self) -> list:
        """
        Get requested core Courses.
        """
        return self.reqCores
    
    def getReqElectives(self) -> list:
        """
        Get requested elective Courses.
        """
        return self.reqElectives
    
    def getReqOff(self) -> list:
        """
        Get period numbers of requested off periods.
        """
        return self.reqOffPeriods
    
    def removeReqCore(self, core: Course):
        """
        Removes requested core Course.
        """
        if core in self.reqCores:
            self.reqCores.remove(core)
            self.reqAll.remove(core)
    
    def removeReqElective(self, elective: Course):
        """
        Removes requested elective Course.
        """
        if elective in self.reqElectives:
            self.reqCores.remove(elective)
            self.reqAll.remove(elective)
    
    def removeReqOff(self, off: int):
        """
        Removes requested off period (int).
        """
        if off in self.reqOffPeriods:
            self.reqCores.remove(off)
            self.reqAll.remove(off)
    
    def getReqVector(self, allCourseCodes: list):
        """
        Returns request vector from a list of all course codes.
        """
        ret = []
        for x in allCourseCodes:
            if x in self.reqAll:
                ret.append(1)
            else:
                ret.append(0)
        return ret
    
    def getReqCheck(self):
        """
        Returns a generator checking if the requests all appear.
        """
        currScheduleVals = list(self.schedule.getSections().values())
        for course in self.reqAll:
            yield (currScheduleVals.count(course) == self.reqAll.count(course))

    def getConstraints(self, allCourses: list):
        """
        Yields constraints checking if each of the requested courses appear.
        """
        for index, courseCode in enumerate(allCourses):
            isRequested = 0
            if courseCode in self.reqAll: isRequested = 1
            
            ret = []
            for period in self.schedule.lpVars.keys():
                ret.append(self.schedule.lpVars[period][index])
            
            yield (summation(ret) == isRequested)

    

            
