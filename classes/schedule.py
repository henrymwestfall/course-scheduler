from __future__ import annotations
from typing import TYPE_CHECKING, List
from copy import deepcopy
from pulp import LpVariable, LpAffineExpression
from .course import CourseType, Course, Section
if TYPE_CHECKING:
    from .individual import Individual
    from .student import Student
    from .teacher import Teacher

# Class for storing the schedule associated with any sort of Individual. Uses a dictionary in order to prevent length overflows.
class Schedule:
    variable_format = "Individual_{tag}_Period_{period}_Course_{course}"
    token_order = ("tag", "period", "course")

    def __init__(self, tag: int, courseLength: int):
        self.sections = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        self.lpVars = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        self.tag = tag
        for period in self.lpVars.keys():
            ret = []
            for course in range(0, courseLength):
                name = self.createVariableName(tag, period, course)
                newVar = LpVariable(name, lowBound=0, upBound=1, cat="Integer") # add constraining values and type
                ret.append(newVar)
            self.lpVars[period] = ret

    def createVariableName(self, tag, period, course):
        """
        Return a variable name based on tag, period, and course
        as determined by predefined format.
        """

        return self.variable_format.format(tag=tag, period=period, course=course)

    def parseVariableName(self, variable_name):
        """
        Parse a variable name and return a dictionary mapping token names to values.
        Return the resulting dictionary.
        """

        template_tokens = self.variable_format.split("_")
        information_token_indices = [i for i, token in enumerate(template_tokens) if "{" in token]
        variable_name_tokens = variable_name.split("_")
        token_values = [token for i, token in enumerate(variable_name_tokens) if i in information_token_indices]
        tokens = {self.token_order[i]: token_value for i, token_value in enumerate(token_values)}
        return tokens

    def __str__(self):
        ret = deepcopy(self.sections)
        for period in ret.keys():
            ret[period] = str(ret[period])
        return str(ret)

    def getOpenPeriods(self) -> List[int]:
        """
        Returns list of open periods (ints).
        """
        ret = []
        for period in self.sections.keys():
            if self.sections[period] == None:
                ret.append(period)
        return ret
    
    def getSections(self) -> dict:
        """
        Returns dict of current sections.
        """
        return self.sections
    
    def addSection(self, newSection: Section) -> bool:
        """
        Adds a section at position pos. Does not work if the period is already filled. Returns True if successfully completed.
        """
        pos = newSection.period
        if self.sections[pos]==None and newSection not in self.sections.values():
            self.sections[pos] = newSection
            return True
        return False
    
    def removeSection(self, section: Section):
        """
        Removes a section by the Section object. Replaces with None.
        """
        pos = section.period
        if self.sections[pos] == section:
            self.sections[pos] = None

    def getValidityConstr(self):
        """
        Yields expressions of if periods have 0 or 1 class.
        """
        for period in self.sections.keys():
            section = self.sections[period]
            hasClass = 0
            if section != None and section.courseType != CourseType.OFF:
                hasClass = 1
            expr = [(var, 1) for var in self.lpVars[period]]
            yield (LpAffineExpression(expr) <= hasClass)

    def haveTeachers(self):
        """
        Checks if all Sections have a qualified teacher.
        """
        for section in self.sections.values():
            if section != None and section.courseType != CourseType.OFF:
                yield section.isValid()
                