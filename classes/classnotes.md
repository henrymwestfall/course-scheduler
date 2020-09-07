# ``course.py``
- Lines 1-9: 
  - First, the imports from package to package, in order to provide proper type hinting and as actual dependencies
  - The ``__future__`` and ``typing`` imports are for type hinting
  - ``utils`` for a cleaner way to sum variables

## ``CourseType``
- Enumeration for course type

## ``Course``
- Line 22: ``__slots__`` to lock class parametres and use less memory
- Lines 23-28: Initialising class components
  - ``_courseCode``: course code
  - ``_qualifiedTeachers``: ``Teacher``s qualified to teach the class
  - ``_potentialPeriods``: period numbers the ``Course`` can be in
  - ``_reqTotalStudents``: total number of students requesting the ``Course``
  - ``_courseType``: course type
- Lines 31-41: ``__eq__`` returns whether another ``Course`` has the same ``_courseCode`` (therefore the same)
- Lines 43-44: ``__repr__`` returns a string representation of the ``Course``
- Lines 46-113: Setters/Getters/simple help functions for interacting with ``_courseCode``, ``_qualifiedTeachers``, ``_potentialPeriods``, ``_reqTotalStudents``, ``_courseType``; and to spawn a ``Section`` based off the ``Course``
  - The teacher-related ones add/remove potential periods and check for qualification, hence their length
- Lines 115-125: ``getGlobalConstr`` generates a constraint ensuring that if there are students attending (``attending``), then a teacher is teaching that course during any period (``ret``)

## ``Section``
- Line 130: ``__slots__`` to lock class parametres and use less memory
- Lines 131-136:
  - ``_courseCode``: course code
  - ``_courseType``: course type
  - ``_instructor``: ``Teacher`` teaching the class
  - ``_period``: period number
  - ``_students``: ``Student``s in the class
- Lines 138-148: ``__str__`` returns a string representation of the ``Section``
- Lines 150-160: ``__eq__`` returns whether another ``Section`` is equal (in all parametres) with the current ``Section``
- Lines 162-234: Setters/Getters/simple help functions for interacting with ``_courseCode``, ``_courseType``, ``_instructor``, ``_period``, ``_students``
- Lines 236-245: ``isValid`` returns whether each of the values is populated, and if the instructor is qualified
- Lines 247-252: ``getClassSizeConstr`` returns the variables of students for the exact period and course code, as well as the instructor variable for the exact period and course code


# ``individual.py``
- Lines 1-8: 
  - First, the imports from package to package, in order to provide proper type hinting and as actual dependencies
  - The ``__future__`` and ``typing`` imports are for type hinting
  - ``pulp`` is to interface with the actual problem
  - ``utils`` for a cleaner way to sum variables

## ``Individual``
- Line 12: ``__slots__`` to lock class parametres and use less memory
- Lines 13-17: Initialising class components
  - ``_tag`` for identification
  - ``_schedule`` to store a ``Schedule`` object
  - ``_reqOffPeriods`` to store number of requested off periods
  - ``_allCourses`` for a list of all course codes for convenience
- Lines 19-22: ``__str__`` reutnr a string representation of the ``Individual``
- Lines 24-55: Setters/Getters/simple help functions for interfacing with ``_schedule``, ``_reqOffPeriods``
- Lines 57-59: ``getConstraints`` interfaces with the other constraint access methods
- Lines 61-68: ``getPeriodAttendanceConstraints`` generates a series of constraints ensuring that the sum of the ``LpVariable``s in each period isn't greater than 1 (would mean more than 1 section at a time)
- Lines 70-88: ``createSections`` creates all sections relevant to the ``_schedule``, returning a list
- Lines 90-97: ``addToSection`` provides indication that an ``addToSection`` method should exist

# ``teacher.py``
- Lines 1-10: 
  - First, the imports from package to package, in order to provide proper type hinting and as actual dependencies
  - The ``__future__`` and ``typing`` imports are for type hinting.
  - ``pulp`` is to interface with the actual problem
  - ``utils`` for a cleaner way to sum variables

## ``Teacher``
- Lines 13-16: Initialising class components
  - ``_qualifications`` to make sure they are able to teach the class
  - ``_openPeriods`` to make sure they have the time to teach the class
- Lines 18-77: Setters/Getters/simple help functions for interfacing with ``_schedule``, ``_qualifications``, ``_openPeriod``
- Lines 88 - 96: ``getQualificationVector`` returns qualification vector of qualifications over ``_allCourses`` by changing an existing list (eager). 0 represents unqualified, 1 represents qualified
- Lines 98-108: ``getConstraints`` interfaces with the other constraint access methods
- Lines 111-128: ``getQualifiedTeachingConstraints`` generates a series of constraints to determine whether teachers are qualified for the sections they teach: qualification is indicated by ``isQualified``, then the variables associated with the course's ``courseCode`` across all periods are compared. Having a sum of variables greater than ``isQualified`` is bad - teacher teaching a section they're unqualified for. But they can also be qualified for something they're not teaching
- Lines 130-132: ``addToSection`` adds the teacher to a section
- Lines 134-138: ``getOpenScore`` returns number of off periods, intended to be used for teachers who only wanted to teach a certain number of classes

# ``student.py``
- Lines 1-10: 
  - First, the imports from package to package, in order to provide proper type hinting and as actual dependencies
  - The ``__future__`` and ``typing`` imports are for type hinting
  - ``pulp`` is to interface with the actual problem
  - ``matplotlib`` is for graphing results
  - ``utils`` for a cleaner way to sum variables

## ``Student``
- Line 13 - 18: Initialising class components
  - ``_grade`` (planned feature) to prioritise grade for class selection
  - ``_reqAll`` to store requested courses
  - ``_altElectives`` for alternate elective choices
- Lines 19 - 75: Setters and getters for ``_schedule``, ``_grade``, ``_reqAll``, ``_altElectives``. Some do tag checking for specific results
- Lines 77-90: ``getReqVector`` returns a vector for requests to see if they're satisfied by appending to a list. 0 represents unfulfilled, 1 represents fulfilled
- Lines 92-102: ``getConstraints`` interfaces with the other constraint access methods.
- Lines 104-120: ``getRequestCheckConstraints`` generates a series of constraints to determine whether the requested courses appear: its appearance is indicated by ``isRequested``, then the variables associated with the course's ``courseCode`` across all periods are added to the other side of the equation. Having a sum of variables different from ``isRequested`` is bad: an unrequested class is showing up then
- Lines 122-124: ``addToSection`` adds the student to a section
- Lines 126-134: ``getOpenScore`` returns the number of requested off periods fulfilled by taking the number of common periods between requested off periods and those actually in the schedule
- Lines 136-145: ``getElectiveCost`` returns the variables associated with requested electives across all periods, as a maximised parametre within the final solution
- Lines 147-153: ``addAltElective``, ``removeAltElective`` are mechanisms for adding alternate electives
- Lines 155-170: ``requestFreqHist`` plots a pie chart of satisfied requests to unsatisifed requests

# ``schedule.py``
- Lines 1-10: 
  - First, the imports from package to package, in order to provide proper type hinting and as actual dependencies
  - The ``__future__`` and ``typing`` imports are for type hinting
  - ``pulp`` is to interface with the actual problem
  - ``numpy`` is used to store the arrays of ``LpVariable``s
  - ``copy`` is utilised to deepcopy dictionaries

## ``Schedule``
- Lines 14-16: Constant definitions
- Line 18: ``__slots__`` to lock class parametres and use less memory
- Lines 19-31: Initialising class components
  - ``_lpVars`` as the initial array of ``periodNo``x``courseCode``
  - ``_tag`` to (just in case) associate an individual with the schedule
  - A for loop is used to make ``_lpVars`` an array of ``LpVariable``s that's ``periodNo``x``courseCode``
- Lines 33-39: ``createVariableName``: function for formatting variable names
- Lines 54-58: ``__str__`` returns string representation of schedule information, using the string representations of each ``Section``
- Lines 60-68: ``getOpenPeriods`` returns empty periods. If there is no scheduled ``Section`` during a period number, the period is empty
- Lines 70-74: ``getSections`` returns raw sections
- Lines 76-84: ``addSection`` adds a section to a period, returning a boolean of success.
- Lines 86-92: ``removeSection`` removes a section, or does nothing if the section is empty
- Lines 94-104: ``getValidityConstr`` returns constraints on number of classes per period. If no class should be then (``hasClass == 0``), the ``LpVars`` under that period should be ``<=`` 0. The same applies for when there is a class (``hasClass == 1``)
- Lines 106-112: ``haveTeachers`` checks whether each of the sections is valid (qualified teacher, period set properly, has more than one student)
