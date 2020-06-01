from schedule import Schedule
from course import CourseType, Course, Section
# Base class Individual and inheriting classes Student and Teacher for storing information for people.
class Individual:
    def __init__(self, tag: int):
        self.tag = tag
        self.schedule = Schedule(tag)
        self.reqOffPeriods = 1
    
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
    
    def offDelta(self):
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
    def __init__(self, tag: int, qualifications: list, openPeriods: list):
        super().__init__(tag)
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
    

class Student(Individual):
    def __init__(self, tag: int, grade: int):
        super().__init__(tag)
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
            self.reqElectives.append(course)
            self.reqAll.append(newElective)
    
    def addReqOffPeriod(self, newOff: int):
        """
        Adds a requested off period.
        """
        # TODO: Will passing int break anything?
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
    

            
