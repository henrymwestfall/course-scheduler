from course import CourseType, Course, Section
from individual import Teacher, Student, Individual
# Class for storing the schedule associated with any sort of Individual. Uses a dictionary in order to prevent length overflows.
class Schedule:
    def __init__(self, tag: int):
        self.sections = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        self.tag = tag
    
    def getOpenPeriods(self) -> list:
        """
        Returns list of open periods (ints).
        """
        ret = []
        for period in self.sections.keys():
            if self.section[period] == None:
                ret.append(period)
        return ret
    
    def getSections(self) -> dict:
        """
        Returns dict of current sections.
        """
        return self.sections
    
    def addSection(self, newSection: Section, pos: int) -> bool:
        """
        Adds a section at position pos. Does not work if the period is already filled. Returns True if successfully completed.
        """
        if self.sections[pos]==None and newSection not in self.sections.values():
            self.sections[pos] = newSection
            return True
        return False
    
    def removeSection(self, section: Section):
        """
        Removes a section by the Section object. Replaces with None.
        """
        if self.sections[section.period] == section:
            self.sections[section.period] = None

# https://github.com/henrymwestfall/course-scheduler
        