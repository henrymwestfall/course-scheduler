""" Generate problems with optimal solutions to test te solver with. These are
be scalable.

Inputs
- teacher count
- student count
- course count
- pathways/subjects count (fairly abstract but helps generation)
- periods in day
"""

import random

import matplotlib.pyplot as plt
import numpy as np

from classes.teacher import Teacher
from classes.student import Student
from classes.course import Course, CourseType


class ToyProblem:
    def __init__(self, num_teachers, num_students, num_courses, num_periods=8, num_pathways=1):
        # initialize starting tag
        self.tag = 0
        self.tags = self.tag_generator()
        
        self.num_teachers = num_teachers
        self.num_students = num_students
        self.num_courses = num_courses
        self.num_periods = num_periods
        self.num_pathways = num_pathways

        # create courses and pathways
        self.all_courses, self.pathways = self.create_courses_and_pathways()

        # create students and teachers
        self.teachers = self.create_blank_teachers()
        self.students = self.create_blank_students()

        # Teachers can teach a specific pathway.
        # students choose from all pathways.
        for t in self.teachers:
            quals = random.choice(self.pathways)
            t.addQualifications(quals)
        for s in self.students:
            reqs = self.create_request_list()
            s.requestAll(reqs)


    def tag_generator(self):
        while True:
            yield self.tag
            self.tag += 1

    @property
    def next_tag(self):
        return next(self.tags)

    def create_courses_and_pathways(self):
        """
        Return a list of course objects and a list of pathways. Pathways are
        sequences of courses where earlier courses in the sequence are 
        prerequisites for later courses in the sequence.
        """

        all_courses = [Course(c, CourseType.CORE) for c in range(self.num_courses)]
        pathways = [[] for _ in range(self.num_pathways)]
        for c in all_courses:
            # add it to the shortest pathway to keep them mostly even
            min(pathways, key=lambda p: len(p)).append(c)
        return all_courses, pathways

    def create_blank_individuals(self, count, individual_type):
        """
        Create a number of blank individuals.
        """

        individuals = []
        for _ in range(count):
            individuals.append(individual_type(self.next_tag, self.all_courses))
        return individuals

    def create_blank_teachers(self):
        return self.create_blank_individuals(self.num_teachers, Teacher)

    def create_blank_students(self):
        return self.create_blank_individuals(self.num_students, Student)

    def create_request_list(self):
        course_list = []

        shortest_pathway_length = len(min(self.pathways, key=lambda p: len(p)))
        level = random.randint(0, shortest_pathway_length - 1)

        for pathway in self.pathways:
            # create selection weights
            weights = []
            for index, _ in enumerate(pathway):
                weights.append(max([3 - abs(level - index), 0]))
            sum_weights = sum(weights)
            weights = [w / sum_weights for w in weights]
            
            course = np.random.choice(pathway, p=weights)
            course_list.append(course)
        
        return course_list